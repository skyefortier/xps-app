OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e251-14ca-7613-a990-dd84c24adea9
--------
user
Re-review unit 4 (the background twins), round 2: branch fix-background-twins. The round-1 fixes are the latest commit (git diff cbf3058..HEAD); the whole unit is git diff 895f323..HEAD. Round-1 verdicts: docs/autofit/codex/background_twins_verdict_run{A,B}.md; the round-1 prompt (brief, sites, measurement): docs/autofit/codex/background_twins_review_prompt.txt. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-1 FINDINGS AND FIXES (plan section 4, verbatim):

**Round 1 — NO-GO ×2** (`background_twins_verdict_run{A,B}.md`; both first
confirmed the parity test fails on the unfixed page exactly as claimed):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: the clamp, combined with the JS's zero start and its index-linear fallback when the net integral vanishes, reached a DIFFERENT fixed point from fitting.py on data that dip below the baseline — `[10,5,5,17,20]`: fitting.py keeps the straight line `[10,12.5,15,17.5,20]`, the JS gave `[10,10,10,15,20]` (33 % of the span); descending and uniform-grid cases 57 %; at every iteration count | the JS Shirley now runs fitting.py's iteration step for step (row S4); the reproducers are parity tests at 5, 50 and 200 iterations |
| 2 | MINOR: CLAUDE.md claimed parity for linear without Task 4's non-uniform-grid exception (index vs energy interpolation, 16.7 % on `[0,1,3]`) | the claim is qualified to the tested cases; the linear gap is pinned as a known gap (not this unit) |


TRY TO BREAK
a. The new shirleyBackground against fitting.shirley_background line by line: the initial line (Python's np.linspace on the ascending copy vs the JS index line on the array as given — equal for descending input?), the cumulative integral's direction and endpoints, `total <= 0` (Python breaks keeping B; the JS breaks keeping bg — including on the FIRST iteration, where both keep the straight line), the 1e-6 stop (Python compares against B_prev after assignment), NaN / Infinity in the data, n = 2, equal energies (zero-width steps), non-uniform and descending grids, a maxIter of 0 or 1 (the UI can send 1).
b. Anything that depended on the OLD JS iteration (a zero start): the UI's iteration-count semantics, tests or fixtures pinning a JS background, smartExperimentalBackground / shirleyLinearBackground if they call shirleyBackground, the local engine, Batch Fit, stack Path B, saved bgIntensity re-use.
c. The new tests: non-vacuous (fail on cbf3058's page), the linear known-gap pin, the tolerance.
d. Docs vs code vs measurement.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll compare the fixes with Python and the round-1 criteria, probe edge cases and downstream callers, then give a ranked verdict within this run.
exec
/bin/zsh -lc "pwd; git status --short; git diff --stat cbf3058..HEAD; git diff --stat 895f323..HEAD; rg --files -g 'AGENTS.md' -g '*background_twins*' -g '*fitting*' -g '*parity*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 4ms:
fitting.py
xps-fitting-tool.html
autofit/parity.py
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
tests/test_legacy_parity.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_c1s_parity_battery.py
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_u4f_parity_battery.py
tests/js/local_lm_server_parity_backend.py
tests/js/background_parity_backend.py
tests/js/lineshape_parity_backend.py
tests/js/background_parity.test.js
tests/js/lineshape_parity.test.js
docs/autofit/codex/background_twins_review_prompt.txt
docs/autofit/codex/background_twins_verdict_runB.md
docs/autofit/codex/background_twins_r2_verdict_runB.md
docs/autofit/codex/background_twins_recheck_prompt.txt
docs/autofit/codex/background_twins_r2_verdict_runA.md
docs/autofit/codex/background_twins_verdict_runA.md

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; rg --files --hidden -g AGENTS.md -g '"'"'!node_modules'"' -g '"'!.git'"'; cat docs/autofit/codex/background_twins_review_prompt.txt; cat docs/superpowers/plans/2026-09-27-background-twins.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
Review unit 4 (the background twins): branch fix-background-twins, stacked on fix-noise-floor-scale-free (F3). Review git diff 895f323..HEAD (895f323 is the F3 commit unit 4 was cut from): templates/index.html (shirleyBackground, smartBackground, one line of computeBackgroundCore), tests/js/background_parity.test.js, tests/js/background_parity_backend.py, CLAUDE.md, docs/superpowers/plans/2026-09-27-background-twins.md. Task 4's investigation: docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "the background parity test plus the two JS fixes (JS shirleyBackground missing the net-signal-at-zero clamp; JS smart clamping against the averaged array instead of raw). shirley_linear is de-listed — pin its divergence as a known gap, don't fix it."

PLAN SECTIONS 1-3 (sites, measurement, tests), verbatim:

## 1. Sites

| # | site | before | after |
|---|---|---|---|
| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg`: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | `max(intensity − bg, 0)` in both integrals, as `fitting.shirley_background` (Proctor–Sherwood); the iteration scheme is otherwise untouched (the JS was already order-invariant: descending input gives the same curve as fitting.py's ascending copy) |
| S5 | `smartBackground(be, intensity, maxIter, rawIntensity)` + `computeBackgroundCore` | clamps `min(shirley, averaged data)` | clamps against the RAW slice (`rawIntensity`, default `intensity`), as `fitting.smart_background`: averaging only ever moves the background, never the reported net counts |
| — | `shirley_linear` | order-sensitive (27–33 % of the span on descending grids, Task 4 cause 3) | UNCHANGED, de-listed (disabled, hidden); the divergence is pinned as a known gap |
| — | not changed | the UI's Shirley iteration count (default 5) vs the server's convergence (tolerance 1e-6, ≤ 200) — Part 5 of the sealed-fit-record memo | |

Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
what the local engine (Batch Fit, fallback) fits against, and what stack
Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
never touch them.

## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)

Max |JS − server| as % of the intensity span:

| method | endpoint avg | iterations | before | after |
|---|---|---|---|---|
| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
| shirley | 10 | 200 | 0.078 % | 0.0000 % |
| smart | 1 | 200 | 0.047 % | 0.0000 % |
| smart | 10 | 200 | **1.19 %** | 0.0000 % |
| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.016–0.019 % (unconverged iteration: Part 5, not this unit) |

## 3. Tests

`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
(fitting.py's own functions, never a reimplementation): shirley, smart,
smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
`computeBackgroundCore` at a converged iteration count, every case within
1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
ascending grids, still diverges on descending ones (pinned; the test fails if
the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.


TRY TO BREAK
a. The clamp: exactly fitting.shirley_background's fixed point (the Python works on an ascending copy, starts from a linear guess and stops at tol; the JS starts from zeros and runs maxIter; the total <= 0 branch — Python breaks keeping the previous B, the JS falls back to an index-linear fraction); non-uniform grids; flat or all-below-background data; n = 2.
b. smart: the raw clamp with averaging, every caller of smartBackground (any that passes 3 arguments and now clamps against the averaged copy?); smart_exp and shirley_linear untouched.
c. Blast radius: every consumer of the JS background (display, fitResult.bgIntensity frozen at fit time, saves, the local engine, stack Path B, Batch Fit, Find Peaks' preview, the ROI hint / anything else) — does anything pin the OLD curve (tests, fixtures, saved-file readers comparing)?
d. The parity test: non-vacuous (fails on the unfixed page), tolerance justified, the bridge calls fitting.py's own functions exactly as run_fit does for the anchor window, the committed real case actually loaded; the shirley_linear pin (would it catch the gap closing? the de-listing assertion).
e. Docs vs code vs measurement.

Finish with VERDICT: GO or VERDICT: NO-GO.# Unit 4 — the background twins: two JS fixes and a pinned parity test (2026-09-27)

Branch `fix-background-twins`, stacked on `fix-noise-floor-scale-free` (F3):
deploy F2 → unit 2 → F3 → unit 4. It touches only `shirleyBackground`,
`smartBackground` and one line of `computeBackgroundCore`; it can be rebased
onto main alone.

Owner's brief (2026-09-27): "the background parity test plus the two JS
fixes (JS shirleyBackground missing the net-signal-at-zero clamp; JS smart
clamping against the averaged array instead of raw). shirley_linear is
de-listed — pin its divergence as a known gap, don't fix it." Source: Task 4
(`docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md`), whose
causes S4 and S5 were proven by exact reconstruction.

## 1. Sites

| # | site | before | after |
|---|---|---|---|
| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg` from a ZERO start, with an index-linear fraction when the integral vanishes: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | fitting.py's iteration step for step (Codex round 1: the clamp alone, on the old start and fallback, reached yet another fixed point on data that dip below the baseline): the straight line between the endpoints as the first guess, `max(intensity − bg, 0)`, the background KEPT when no net signal is left, the same 1e-6 stop; one O(n) cumulative integral per iteration (was O(n²)). Array order does not matter (the JS form is fitting.py's ascending-copy form mirrored). |
| S5 | `smartBackground(be, intensity, maxIter, rawIntensity)` + `computeBackgroundCore` | clamps `min(shirley, averaged data)` | clamps against the RAW slice (`rawIntensity`, default `intensity`), as `fitting.smart_background`: averaging only ever moves the background, never the reported net counts |
| — | `shirley_linear` | order-sensitive (27–33 % of the span on descending grids, Task 4 cause 3) | UNCHANGED, de-listed (disabled, hidden); the divergence is pinned as a known gap |
| — | not changed | the UI's Shirley iteration count (default 5) vs the server's convergence (tolerance 1e-6, ≤ 200) — Part 5 of the sealed-fit-record memo | |

Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
what the local engine (Batch Fit, fallback) fits against, and what stack
Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
never touch them.

## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)

Max |JS − server| as % of the intensity span:

| method | endpoint avg | iterations | before | after |
|---|---|---|---|---|
| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
| shirley | 10 | 200 | 0.078 % | 0.0000 % |
| smart | 1 | 200 | 0.047 % | 0.0000 % |
| smart | 10 | 200 | **1.19 %** | 0.0000 % |
| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.0035–0.005 % (unconverged iteration: Part 5, not this unit) |
| shirley / smart on below-baseline data (the round-1 reproducers, incl. non-uniform grids) | 1 | 5 / 50 / 200 | — (with the clamp alone: 33–58 %) | within 1e-6 at every count |

## 3. Tests

`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
(fitting.py's own functions, never a reimplementation): shirley, smart,
smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
`computeBackgroundCore` at a converged iteration count, every case within
1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
ascending grids, still diverges on descending ones (pinned; the test fails if
the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.

## 4. Codex rounds

**Round 1 — NO-GO ×2** (`background_twins_verdict_run{A,B}.md`; both first
confirmed the parity test fails on the unfixed page exactly as claimed):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: the clamp, combined with the JS's zero start and its index-linear fallback when the net integral vanishes, reached a DIFFERENT fixed point from fitting.py on data that dip below the baseline — `[10,5,5,17,20]`: fitting.py keeps the straight line `[10,12.5,15,17.5,20]`, the JS gave `[10,10,10,15,20]` (33 % of the span); descending and uniform-grid cases 57 %; at every iteration count | the JS Shirley now runs fitting.py's iteration step for step (row S4); the reproducers are parity tests at 5, 50 and 200 iterations |
| 2 | MINOR: CLAUDE.md claimed parity for linear without Task 4's non-uniform-grid exception (index vs energy interpolation, 16.7 % on `[0,1,3]`) | the claim is qualified to the tested cases; the linear gap is pinned as a known gap (not this unit) |


exec
/bin/zsh -lc "rg -n 'VERDICT:|BLOCKER|MAJOR|MINOR|Findings|findings' docs/autofit/codex/background_twins_verdict_runA.md docs/autofit/codex/background_twins_verdict_runB.md | tail -70; rg -n 'def (shirley_background|linear_background|smart|shirley_linear)|function (shirleyBackground|smartExperimentalBackground|shirleyLinearBackground)|shirleyBackground\\(|bgIntensity|maxIter' fitting.py templates/index.html | head -160" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
docs/autofit/codex/background_twins_verdict_runA.md:13:Review unit 4 (the background twins): branch fix-background-twins, stacked on fix-noise-floor-scale-free (F3). Review git diff 895f323..HEAD (895f323 is the F3 commit unit 4 was cut from): templates/index.html (shirleyBackground, smartBackground, one line of computeBackgroundCore), tests/js/background_parity.test.js, tests/js/background_parity_backend.py, CLAUDE.md, docs/superpowers/plans/2026-09-27-background-twins.md. Task 4's investigation: docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/background_twins_verdict_runA.md:65:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/background_twins_verdict_runA.md:67:I’ll review the diff and callers, check the parity bridge against `run_fit`, and probe the edge cases you listed. I’ll keep it read-only and finish with ranked findings and a verdict.
docs/autofit/codex/background_twins_verdict_runA.md:3987:1. **MAJOR — The clamp introduces a different converged Shirley result on below-baseline data.** [templates/index.html:4424](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4424)
docs/autofit/codex/background_twins_verdict_runA.md:4000:2. **MINOR — The new documentation overstates parity for linear backgrounds.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748)
docs/autofit/codex/background_twins_verdict_runA.md:4006:**VERDICT: NO-GO.**
docs/autofit/codex/background_twins_verdict_runA.md:4009:1. **MAJOR — The clamp introduces a different converged Shirley result on below-baseline data.** [templates/index.html:4424](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4424)
docs/autofit/codex/background_twins_verdict_runA.md:4022:2. **MINOR — The new documentation overstates parity for linear backgrounds.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748)
docs/autofit/codex/background_twins_verdict_runA.md:4028:**VERDICT: NO-GO.**
docs/autofit/codex/background_twins_verdict_runB.md:13:Review unit 4 (the background twins): branch fix-background-twins, stacked on fix-noise-floor-scale-free (F3). Review git diff 895f323..HEAD (895f323 is the F3 commit unit 4 was cut from): templates/index.html (shirleyBackground, smartBackground, one line of computeBackgroundCore), tests/js/background_parity.test.js, tests/js/background_parity_backend.py, CLAUDE.md, docs/superpowers/plans/2026-09-27-background-twins.md. Task 4's investigation: docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/background_twins_verdict_runB.md:65:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/background_twins_verdict_runB.md:67:I’ll review the diff and backend call path, then test edge cases and the parity test’s sensitivity to the two fixes. I’ll keep the review read-only and finish with ranked findings and a verdict.
docs/autofit/codex/background_twins_verdict_runB.md:330:`docs/findings/2026-09-26-public-request-ceiling.md`.)
docs/autofit/codex/background_twins_verdict_runB.md:512:(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).
docs/autofit/codex/background_twins_verdict_runB.md:695:the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
docs/autofit/codex/background_twins_verdict_runB.md:705:DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
docs/autofit/codex/background_twins_verdict_runB.md:4686:1. **MAJOR — The new clamp interacts with the existing initialization/fallback to produce persistent cycles.** [templates/index.html:4428](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4428), particularly the fallback at line 4430.
docs/autofit/codex/background_twins_verdict_runB.md:4699:2. **MINOR — The new documentation overstates the parity guarantee.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748).
docs/autofit/codex/background_twins_verdict_runB.md:4705:**VERDICT: NO-GO**
docs/autofit/codex/background_twins_verdict_runB.md:4708:1. **MAJOR — The new clamp interacts with the existing initialization/fallback to produce persistent cycles.** [templates/index.html:4428](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4428), particularly the fallback at line 4430.
docs/autofit/codex/background_twins_verdict_runB.md:4721:2. **MINOR — The new documentation overstates the parity guarantee.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748).
docs/autofit/codex/background_twins_verdict_runB.md:4727:**VERDICT: NO-GO**
fitting.py:338:def shirley_background(
fitting.py:402:def smart_background(
fitting.py:422:def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
fitting.py:428:def smart_experimental_background(
fitting.py:484:def shirley_linear_background(
templates/index.html:4408:function shirleyBackground(be, intensity, maxIter) {
templates/index.html:4422:  for (let iter = 0; iter < maxIter; iter++) {
templates/index.html:4445:function smartBackground(be, intensity, maxIter, rawIntensity) {
templates/index.html:4456:  const shir = shirleyBackground(be, intensity, maxIter);
templates/index.html:4466:function smartExperimentalBackground(be, intensity, maxIter, nAvg) {
templates/index.html:4485:  for (let iter = 0; iter < maxIter; iter++) {
templates/index.html:4621:function shirleyLinearBackground(be, intensity, maxIter, nAvg) {
templates/index.html:4647:  for (let iter = 0; iter < maxIter; iter++) {
templates/index.html:4679:  if (state.fitResult) state.fitResult.bgIntensity = null;
templates/index.html:4755:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
templates/index.html:5827:  const bgIntensity = computeBackground(be, inten);
templates/index.html:5828:  const netAmplitude = Math.max(intensityValue - bgIntensity[closestIdx], 100);
templates/index.html:7373:    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
templates/index.html:7739:    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
templates/index.html:8146:  const bgIntensity = computeBackground(be, inten);
templates/index.html:8147:  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:8270:                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
templates/index.html:8312:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
templates/index.html:8473:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
templates/index.html:8474:  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
templates/index.html:8483:      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
templates/index.html:8484:      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
templates/index.html:8490:  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
templates/index.html:8677:  for (let iter = 0; iter < maxIter && !converged; iter++) {
templates/index.html:8781:  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);
templates/index.html:8821:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
templates/index.html:9281://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
templates/index.html:9283://   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
templates/index.html:9325:      && Array.isArray(fr.bgIntensity)
templates/index.html:9326:      && fr.bgIntensity.length === fr.be.length) {
templates/index.html:9329:    bg = fr.bgIntensity.slice();
templates/index.html:9811:                     Array.isArray(state.fitResult.bgIntensity) &&
templates/index.html:9812:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
templates/index.html:9818:  const plotBG = haveFit ? state.fitResult.bgIntensity
templates/index.html:10565:  const bgIntensity = computeBackground(be, inten);
templates/index.html:10567:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:10572:  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);
templates/index.html:10623:    background: bgIntensity,
templates/index.html:10690:        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
templates/index.html:11246:  const bgIntensity = computeBackground(be, inten);
templates/index.html:11258:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:11263:      be[i].toFixed(4), inten[i].toFixed(2), bgIntensity[i].toFixed(2),
templates/index.html:11823:    const bgI = fitResult.bgIntensity;
templates/index.html:14273:      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
templates/index.html:16395:  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
templates/index.html:16402:  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a

exec
/bin/zsh -lc 'git diff cbf3058..HEAD -- templates/index.html tests/js/background_parity.test.js CLAUDE.md; cat tests/js/background_parity_backend.py; cat tests/js/background_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jLSQxPsC' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sCi8xb5s' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 6cd3464..a063dbf 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -745,15 +745,19 @@ starting model as "Fit complete"; see
 
 The page's background twins (`computeBackgroundCore`: what it draws, freezes
 into `fitResult.bgIntensity` at fit time, saves, and what the local engine
-fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
-iteration count for shirley, smart, smart_exp, tougaard and linear, with
-endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
-2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
-against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
+fits against) equal fitting.py's to 1e-6 of the intensity span on the tested
+cases — shirley, smart, smart_exp and tougaard on uniform and non-uniform
+grids, linear on uniform grids, endpoint averaging 1 and 10, and data that
+dip below the baseline (`tests/js/background_parity.test.js`, unit 4
+2026-09-27: the JS Shirley now runs fitting.py's iteration step for step —
+the straight line as the first guess, the net signal clamped at zero, the
+background kept when no net signal is left, the 1e-6 stop — and smart clamps
+against the raw data; Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
 the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
-descending grids; the UI's Shirley iteration count (default 5) leaves
-0.016–0.019 % of the span of unfinished iteration (Part 5 of the
-sealed-fit-record memo).
+descending grids; linear interpolates by index on the page and by energy on
+the server, equal only on uniform grids (Task 4 cause 4); the UI's Shirley
+iteration count (default 5) stops before fitting.py's convergence (Part 5 of
+the sealed-fit-record memo).
 
 Use Shirley for standard core-level regions. Linear only when the
 spectral window is very narrow and featureless.
diff --git a/templates/index.html b/templates/index.html
index 655a50c..b708de7 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4406,31 +4406,38 @@ function evalAllPeaks(beArray, peaks) {
 // BACKGROUND SUBTRACTION
 // ═══════════════════════════════════════════════════
 function shirleyBackground(be, intensity, maxIter) {
+  // fitting.shirley_background's iteration, step for step (unit 4, Codex
+  // round 1): the straight line between the endpoints as the first guess,
+  // the net signal clamped at zero (Proctor–Sherwood), the background KEPT
+  // when no net signal is left, and the same 1e-6 convergence stop. The
+  // clamp alone, on the old zero start and index-linear fallback, reached a
+  // different fixed point on data that dip below the baseline (33–58 % of the
+  // span on small cases). The array order does not matter: the cumulative
+  // integral runs to the array's end and the endpoints are the array's, which
+  // is fitting.py's ascending-copy form mirrored.
   const n = be.length;
   if (n < 2) return new Array(n).fill(0);
   const I0 = intensity[0], I1 = intensity[n - 1];
-  let bg = new Array(n).fill(0);
-
+  let bg = intensity.map((_, i) => I0 + (I1 - I0) * i / (n - 1));
   for (let iter = 0; iter < maxIter; iter++) {
-    const newBg = new Array(n).fill(0);
+    const cum = new Array(n).fill(0);            // cum[i] = ∫ net signal from point i to the array end
+    let sPrev = Math.max(intensity[n - 1] - bg[n - 1], 0);
+    for (let j = n - 2; j >= 0; j--) {
+      const sj = Math.max(intensity[j] - bg[j], 0);
+      cum[j] = cum[j + 1] + 0.5 * (sj + sPrev) * Math.abs(be[j + 1] - be[j]);
+      sPrev = sj;
+    }
+    const total = cum[0];
+    if (!(total > 0)) break;                     // no net signal left: keep the current background
+    let maxChange = 0;
+    const next = new Array(n);
     for (let i = 0; i < n; i++) {
-      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
-      // (Proctor–Sherwood): a noise channel below the background contributes
-      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
-      // integrated the raw difference and converged to a different fixed point,
-      // 0.015–0.24 % of the span away from the background the server fits).
-      let sumRight = 0;
-      for (let j = i; j < n - 1; j++) {
-        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
-      }
-      let sumTotal = 0;
-      for (let j = 0; j < n - 1; j++) {
-        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
-      }
-      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
-      newBg[i] = I1 + (I0 - I1) * frac;
+      next[i] = I1 + (I0 - I1) * cum[i] / total;
+      const d = Math.abs(next[i] - bg[i]);
+      if (d > maxChange) maxChange = d;
     }
-    bg = newBg;
+    bg = next;
+    if (maxChange < 1e-6) break;                 // fitting.py's tolerance
   }
   return bg;
 }
diff --git a/tests/js/background_parity.test.js b/tests/js/background_parity.test.js
index 8c9e728..d7901b0 100644
--- a/tests/js/background_parity.test.js
+++ b/tests/js/background_parity.test.js
@@ -80,6 +80,36 @@ for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
   }
 }
 
+// Codex round 1: data that dip below the baseline. With the clamp but the old
+// zero start and index-linear fallback, the JS reached another fixed point
+// (33–58 % of the span); fitting.py starts from the straight line and keeps it
+// when no net signal is left. Exact small cases, every iteration count.
+const BELOW = [
+  { be: [0, 1, 2, 3, 4], inten: [10, 5, 5, 17, 20] },
+  { be: [3.5, 1.1, 1, 0], inten: [6, 7, 13, 19] },
+  { be: [3, 2, 1, 0], inten: [100, 107, 120, 127] },
+  { be: [0, 1, 3, 6, 10], inten: [10, 5, 5, 17, 20] },
+];
+test('below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)', () => {
+  for (const method of ['shirley', 'smart']) {
+    const server = py({ mode: 'bg', items: BELOW.map(c => ({ method, be: c.be, inten: c.inten, n_avg: 1 })) });
+    BELOW.forEach((c, k) => {
+      for (const it of [5, 50, 200]) {
+        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '1', bgStart: '', bgEnd: '' });
+        const rel = maxRelDiff(js, server[k], span(c.inten));
+        assert.ok(rel <= TOL, `${method} ${JSON.stringify(c.be)} at ${it} iterations: ${rel.toExponential(2)} of the span (js ${js.map(v => v.toFixed(3))}, server ${server[k].map(v => v.toFixed(3))})`);
+      }
+    });
+  }
+});
+
+test('KNOWN GAP (Task 4 cause 4, not this unit): linear interpolates by index on the page, by energy on the server — equal on uniform grids only', () => {
+  const nonUniform = { be: [0, 1, 3], inten: [10, 20, 40] };
+  const server = py({ mode: 'bg', items: [{ method: 'linear', be: nonUniform.be, inten: nonUniform.inten, n_avg: 1 }] })[0];
+  const js = jsBg(nonUniform.be, nonUniform.inten, 'linear', 1);
+  assert.ok(maxRelDiff(js, server, span(nonUniform.inten)) > 0.05, 'still differs on a non-uniform grid — if this starts failing the gap was closed; update the pin and CLAUDE.md');
+});
+
 test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
   const rows = compare('shirley_linear', 1);
   for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
#!/usr/bin/env python3
"""Backend bridge for tests/js/background_parity.test.js (unit 4, 2026-09-27).

stdin {"mode": "cases"} -> the spectra the parity test runs on: seeded
synthetic spectra (a narrow C 1s, a wide U 4f doublet) and the committed real
U 4f Scan_0 (1-GTA UCl4-graphite project), each ascending AND descending.
stdin {"mode": "bg", "items": [{"method", "be", "inten", "n_avg"}...]} -> the
background fitting.py's OWN function returns for each (the functions run_fit
calls for the anchor window, never a reimplementation).
"""
import io
import json
import os
import sys
import zipfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import fitting  # noqa: E402

FUNCS = {
    "shirley": lambda x, y, n: fitting.shirley_background(x, y, n_avg=n),
    "smart": lambda x, y, n: fitting.smart_background(x, y, n_avg=n),
    "smart_exp": lambda x, y, n: fitting.smart_experimental_background(x, y, n_avg=n),
    "shirley_linear": lambda x, y, n: fitting.shirley_linear_background(x, y, n_avg=n),
    "tougaard": lambda x, y, n: fitting.tougaard_background(x, y, n_avg=n),
    "linear": lambda x, y, n: fitting.linear_background(x, y),
}


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _shirley_step(x, c, a, w, h):
    # a loss step under each line, high-BE side (makes Shirley non-trivial)
    return h * a / (1 + np.exp(-(x - c) / (0.4 * w)))


def cases():
    rng = np.random.default_rng(20260927)
    out = []
    x = np.linspace(280.0, 295.0, 101)
    y = rng.poisson(400 + _g(x, 284.5, 6000, 1.0) + _g(x, 286.3, 1200, 1.2) + _shirley_step(x, 284.5, 6000, 1.0, 0.06)).astype(float)
    out.append(("synthetic C 1s, 101 pts", x, y))
    x = np.linspace(370.0, 405.0, 351)
    y = rng.poisson(2000 + _g(x, 380.9, 20000, 1.6) + _g(x, 391.8, 15000, 1.6)
                    + _shirley_step(x, 380.9, 20000, 1.6, 0.08) + _shirley_step(x, 391.8, 15000, 1.6, 0.08)).astype(float)
    out.append(("synthetic U 4f doublet, 351 pts", x, y))
    proj = os.path.join(ROOT, "docs", "autofit", "test_data", "1-GTA UCl4-graphite one set of U doublets.proj.zip")
    if os.path.exists(proj):
        with zipfile.ZipFile(proj) as z:
            man = json.loads(z.read("manifest.json"))
            for sp in man.get("spectra", []):
                if sp.get("name") == "U4f Scan_0":
                    rec = json.loads(z.read(sp["filename"]))
                    be = np.asarray(rec["rawBE"], float) - float(rec.get("ccShift") or 0)
                    out.append(("real U 4f Scan_0 (committed project)", be, np.asarray(rec["rawIntensity"], float)))
                    break
    res = []
    for label, x, y in out:
        asc = np.argsort(x)
        res.append({"label": label + ", ascending", "be": x[asc].tolist(), "inten": y[asc].tolist()})
        res.append({"label": label + ", descending", "be": x[asc][::-1].tolist(), "inten": y[asc][::-1].tolist()})
    return res


def main():
    req = json.load(sys.stdin)
    if req["mode"] == "cases":
        json.dump(cases(), sys.stdout)
        return
    out = []
    for it in req["items"]:
        x = np.asarray(it["be"], float)
        y = np.asarray(it["inten"], float)
        out.append([float(v) for v in FUNCS[it["method"]](x, y, int(it["n_avg"]))])
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
// Unit 4 (2026-09-27): the page's background twins against fitting.py — the
// curve the page draws, saves and fits locally against must be the one the
// server fits against. Task 4 (docs/superpowers/plans/2026-09-02-task4-
// background-twin-parity.md) measured the gaps and proved their causes;
// this unit fixes the two JS bugs it found and PINS the parity:
//   S4 shirley: the JS integrated the raw net signal, fitting.py max(y−B, 0)
//      (0.015–0.24 % of the span at convergence);
//   S5 smart at endpoint averaging > 1: the JS clamped against the averaged
//      copy, fitting.py against the raw data (up to 1 % of the span).
// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
// descending grids (27–33 % of the span, Task 4 cause 3) is pinned as a KNOWN
// GAP, not fixed. Convergence semantics (the UI's Shirley iteration count vs
// the server's tolerance) are Part 5 of the sealed-fit-record memo, not this
// unit: the JS runs at a converged iteration count here.
//
// The JS runs computeBackgroundCore (the page's own dispatcher) extracted
// verbatim; the Python side calls fitting.py's own functions through
// tests/js/background_parity_backend.py.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

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
const PYTHON = (() => {
  for (const c of [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
    if (fs.existsSync(c)) return c;
  }
  return 'python3';
})();
const BRIDGE = path.join(__dirname, 'background_parity_backend.py');
const py = req => JSON.parse(execFileSync(PYTHON, [BRIDGE], { input: JSON.stringify(req), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));

const JS = new Function([
  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
  'linearBackground', 'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
  '\nreturn { computeBackgroundCore };')();
const CONVERGED_ITER = 200;
const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });

const CASES = py({ mode: 'cases' });
const span = y => Math.max(...y) - Math.min(...y);
function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
function compare(method, nAvg) {
  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
}

test('the cases include the committed real U 4f scan, ascending and descending', () => {
  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
});

// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
// difference between 200 JS iterations and the server's 1e-6-count stopping
// tolerance.
const TOL = 1e-6;
for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
  for (const nAvg of [1, 10]) {
    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
    });
  }
}

// Codex round 1: data that dip below the baseline. With the clamp but the old
// zero start and index-linear fallback, the JS reached another fixed point
// (33–58 % of the span); fitting.py starts from the straight line and keeps it
// when no net signal is left. Exact small cases, every iteration count.
const BELOW = [
  { be: [0, 1, 2, 3, 4], inten: [10, 5, 5, 17, 20] },
  { be: [3.5, 1.1, 1, 0], inten: [6, 7, 13, 19] },
  { be: [3, 2, 1, 0], inten: [100, 107, 120, 127] },
  { be: [0, 1, 3, 6, 10], inten: [10, 5, 5, 17, 20] },
];
test('below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)', () => {
  for (const method of ['shirley', 'smart']) {
    const server = py({ mode: 'bg', items: BELOW.map(c => ({ method, be: c.be, inten: c.inten, n_avg: 1 })) });
    BELOW.forEach((c, k) => {
      for (const it of [5, 50, 200]) {
        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '1', bgStart: '', bgEnd: '' });
        const rel = maxRelDiff(js, server[k], span(c.inten));
        assert.ok(rel <= TOL, `${method} ${JSON.stringify(c.be)} at ${it} iterations: ${rel.toExponential(2)} of the span (js ${js.map(v => v.toFixed(3))}, server ${server[k].map(v => v.toFixed(3))})`);
      }
    });
  }
});

test('KNOWN GAP (Task 4 cause 4, not this unit): linear interpolates by index on the page, by energy on the server — equal on uniform grids only', () => {
  const nonUniform = { be: [0, 1, 3], inten: [10, 20, 40] };
  const server = py({ mode: 'bg', items: [{ method: 'linear', be: nonUniform.be, inten: nonUniform.inten, n_avg: 1 }] })[0];
  const js = jsBg(nonUniform.be, nonUniform.inten, 'linear', 1);
  assert.ok(maxRelDiff(js, server, span(nonUniform.inten)) > 0.05, 'still differs on a non-uniform grid — if this starts failing the gap was closed; update the pin and CLAUDE.md');
});

test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
  const rows = compare('shirley_linear', 1);
  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
  const desc = rows.filter(r => /descending/.test(r.label));
  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
});

exec
/bin/zsh -lc "sed -n '295,535p' fitting.py; sed -n '4405,4800p' templates/index.html; rg -n 'shirleyIter|smartBackground\\(|computeBackgroundCore\\(|computeBackground\\(' templates/index.html | head -110" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
        # centre lies OUTSIDE the padded grid, so "the value at the centre"
        # is np.interp's clamped end value — the tail of a curve whose peak
        # is not on the grid, of order 1e-20 once the tapers have acted, and
        # its SIGN decided which of two unrelated curves came back (the
        # max-normalised tail, or that tail divided by ~1e-20; Codex round 2
        # of the unit). Normalise by the curve's maximum instead. A centre
        # inside the padded grid takes the branch below, unchanged.
        peak_val = float(np.max(np.abs(result)))
        if peak_val <= 0.0:
            return np.zeros_like(x)
    else:
        # Interpolate at exact center rather than nearest grid point to avoid
        # normalization error when center falls between data points.
        peak_val = float(np.interp(center, x_padded, ds_conv))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(result))
        if peak_val <= 0.0:
            return np.zeros_like(x)

    result = amplitude * result / peak_val

    # Final safety: suppress any NaN/Inf
    return np.where(np.isfinite(result), result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
    n = len(y)
    if n_avg <= 1 or n < 4:
        return y.copy()
    cap = min(n_avg, n // 4)
    if cap < 1:
        return y.copy()
    out = y.copy()
    out[:cap] = np.mean(y[:cap])
    out[-cap:] = np.mean(y[-cap:])
    return out


def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
    ENTIRE background off those two levels, so a single noisy endpoint
    sample propagates straight into the net area. n_avg=1 = raw endpoints =
    previous behaviour. Callers previously had to pre-average the input
    array themselves via _apply_endpoint_averaging; that convention was
    easy to forget (autofit/engine.py did), so the knob now lives here,
    matching smart_experimental_background / shirley_linear_background.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    if n_avg > 1:
        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]    # background at low‑BE end
    b_high = ys[-1]  # background at high‑BE end

    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.

    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
    applied against the RAW data, not the endpoint-averaged copy, so
    averaging only ever moves the background — never the reported net
    counts.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
    return np.minimum(shir, y)


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Hybrid Shirley + Linear background.

    1. Average *n_avg* points at each endpoint.
    2. Compute a linear baseline between the averaged endpoints.
    3. Subtract the linear baseline → flattened data.
    4. Iteratively compute a Shirley‑like cumulative correction on the
       flattened data, scaled by the endpoint step height.
    5. Add the correction back onto the linear baseline.
    6. Clamp so the background never exceeds the data.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint

    # Linear baseline
    linear = np.linspace(IL, IH, n)

    # Flatten
    flat = ys - linear

    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear

    B = np.zeros(n)
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(flat - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
// ═══════════════════════════════════════════════════
// BACKGROUND SUBTRACTION
// ═══════════════════════════════════════════════════
function shirleyBackground(be, intensity, maxIter) {
  // fitting.shirley_background's iteration, step for step (unit 4, Codex
  // round 1): the straight line between the endpoints as the first guess,
  // the net signal clamped at zero (Proctor–Sherwood), the background KEPT
  // when no net signal is left, and the same 1e-6 convergence stop. The
  // clamp alone, on the old zero start and index-linear fallback, reached a
  // different fixed point on data that dip below the baseline (33–58 % of the
  // span on small cases). The array order does not matter: the cumulative
  // integral runs to the array's end and the endpoints are the array's, which
  // is fitting.py's ascending-copy form mirrored.
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  let bg = intensity.map((_, i) => I0 + (I1 - I0) * i / (n - 1));
  for (let iter = 0; iter < maxIter; iter++) {
    const cum = new Array(n).fill(0);            // cum[i] = ∫ net signal from point i to the array end
    let sPrev = Math.max(intensity[n - 1] - bg[n - 1], 0);
    for (let j = n - 2; j >= 0; j--) {
      const sj = Math.max(intensity[j] - bg[j], 0);
      cum[j] = cum[j + 1] + 0.5 * (sj + sPrev) * Math.abs(be[j + 1] - be[j]);
      sPrev = sj;
    }
    const total = cum[0];
    if (!(total > 0)) break;                     // no net signal left: keep the current background
    let maxChange = 0;
    const next = new Array(n);
    for (let i = 0; i < n; i++) {
      next[i] = I1 + (I0 - I1) * cum[i] / total;
      const d = Math.abs(next[i] - bg[i]);
      if (d > maxChange) maxChange = d;
    }
    bg = next;
    if (maxChange < 1e-6) break;                 // fitting.py's tolerance
  }
  return bg;
}

function smartBackground(be, intensity, maxIter, rawIntensity) {
  // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
  // The Shirley runs on `intensity` (the endpoint-averaged copy); the clamp is
  // against the RAW data (`rawIntensity`, defaulting to `intensity`), as
  // fitting.smart_background does: averaging only ever moves the background,
  // never the reported net counts (Task 4 S5, unit 4 2026-09-27 — at an
  // endpoint average of 10 the two sides differed by up to 1 % of the span at
  // the averaged edges).
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const raw = rawIntensity || intensity;
  const shir = shirleyBackground(be, intensity, maxIter);
  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], raw[i]);
  return shir;
}

// Experimental constrained Shirley background, closer to the public Avantage
// Smart description: the data-constraint is enforced *during* iteration, not as
// a post-hoc clamp.  Where the background would exceed the data, it locks to
// the data and the effective Shirley start moves inward, improving behaviour on
// narrow windows with sloped baselines.
function smartExperimentalBackground(be, intensity, maxIter, nAvg) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);

  // Averaged endpoints
  const cap = Math.min(nAvg || 1, Math.floor(n / 4)) || 1;
  let sL = 0, sR = 0;
  for (let i = 0; i < cap; i++) sL += intensity[i];
  for (let i = n - cap; i < n; i++) sR += intensity[i];
  const I0 = sL / cap;   // left endpoint (index 0, typically high-BE)
  const I1 = sR / cap;   // right endpoint (index n-1, typically low-BE)

  // Step height for the Shirley component
  const step = I0 - I1;

  // bg[i] = background value at point i
  let bg = new Array(n);
  for (let i = 0; i < n; i++) bg[i] = I1 + step * (n - 1 - i) / (n - 1); // linear init

  for (let iter = 0; iter < maxIter; iter++) {
    const prev = bg;
    const newBg = new Array(n);

    // Signal = data above current background, nonneg
    const signal = new Array(n);
    for (let i = 0; i < n; i++) signal[i] = Math.max(intensity[i] - bg[i], 0);

    // Cumulative integral from right (index n-1) to each point i
    const cumRight = new Array(n).fill(0);
    for (let j = n - 2; j >= 0; j--) {
      const dx = Math.abs(be[j + 1] - be[j]);
      cumRight[j] = cumRight[j + 1] + (signal[j] + signal[j + 1]) / 2 * dx;
    }
    const totalInt = cumRight[0];
    if (totalInt <= 0) break;

    // Build unconstrained Shirley background
    for (let i = 0; i < n; i++) {
      newBg[i] = I1 + step * (cumRight[i] / totalInt);
    }

    // Constrain during iteration: where bg exceeds data, lock to data.
    // This effectively moves the Shirley start inward at those points.
    for (let i = 0; i < n; i++) {
      newBg[i] = Math.min(newBg[i], intensity[i]);
    }

    bg = newBg;

    // Convergence check
    let maxDelta = 0;
    for (let i = 0; i < n; i++) {
      const d = Math.abs(bg[i] - prev[i]);
      if (d > maxDelta) maxDelta = d;
    }
    if (maxDelta < 1e-4) break;
  }

  // Final clamp to data (safety)
  for (let i = 0; i < n; i++) bg[i] = Math.min(bg[i], intensity[i]);

  return bg;
}

function linearBackground(be, intensity) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  const bg = [];
  for (let i = 0; i < n; i++) bg.push(I0 + (I1 - I0) * i / (n - 1));
  return bg;
}

// Single-pass Tougaard background — JS twin of fitting.py's
// tougaard_background (keep the two numerically in agreement; pinned by
// tests/js/tougaard_twin.test.js). Universal loss kernel
// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
// Surf. Interface Anal. 11, 453 (1988); kernel max at sqrt(C/3) ≈ 23.4 eV).
// C was long shipped squared (1643*1643) — fixed 2026-07-04 with the backend.
function tougaardBackground(be, intensity, nAvg) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const B = 2866, C = 1643;
  // The one-sided loss sum (j >= i) is physical only on a DESCENDING BE
  // grid (loss contributions come from lower-BE / higher-KE emitters).
  // Normalize to descending internally and flip back, like the backend.
  const flipped = be[0] < be[n - 1];
  const beW = flipped ? [...be].reverse() : be;
  let inW = flipped ? [...intensity].reverse() : intensity;
  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
  // integral assumes the window BEGINS loss-free, so J at the low-BE edge is
  // the zero-loss level. Real windows never satisfy that: the out-of-window
  // inelastic baseline from every lower-BE (higher-KE) transition cannot be
  // reproduced by a window-limited integral, and since K(0) = 0 the bare
  // integral is identically zero at the low-BE edge REGARDLESS of the data —
  // the background dove to ~0 there and a flat window produced phantom
  // signal. Take the low-BE level as a constant offset, run the kernel over
  // the net above it, then anchor the amplitude at the high-BE edge.
  const c0 = inW[n - 1];
  // Local quadrature weights (F2, 2026-07-17): weight each term by its own
  // energy spacing instead of a single dx lifted from the first two points,
  // which silently assumed a uniform grid.
  const w = new Array(n);
  for (let i = 0; i < n; i++) {
    if (i === 0) w[0] = Math.abs(beW[1] - beW[0]);
    else if (i === n - 1) w[n - 1] = Math.abs(beW[n - 1] - beW[n - 2]);
    else w[i] = Math.abs(beW[i + 1] - beW[i - 1]) / 2;
  }
  const bg = new Array(n).fill(0);
  for (let i = 0; i < n; i++) {
    let sum = 0;
    for (let j = i; j < n; j++) {
      const T = Math.abs(beW[j] - beW[i]);
      sum += (B * T) / Math.pow(C + T * T, 2) * (inW[j] - c0) * w[j];
    }
    bg[i] = sum;
  }
  // Amplitude anchor at the HIGH-BE edge (index 0 after normalization):
  // scale so the background meets the measured intensity above the peak —
  // the practical Tougaard criterion (B effectively fitted; C alone sets the
  // kernel shape). Guard: if no net loss signal accumulates at the high-BE
  // edge (bg[0] === 0 — e.g. a flat or empty window) the honest background is
  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
  // whole baseline as net signal (the pre-F1 behaviour). Negative counts
  // (physically invalid input) pass through signed; no clamping here.
  let out;
  if (bg[0] === 0) {
    out = new Array(n).fill(c0);
  } else {
    const scale = (inW[0] - c0) / bg[0];
    out = bg.map(v => c0 + v * scale);
  }
  return flipped ? out.reverse() : out;
}

// Apply endpoint averaging: replace first/last N points with their mean so
// existing Shirley/Smart functions pick up averaged endpoint intensities.
// Returns a new array — does not mutate the input.
function _applyEndpointAveraging(intensity, nAvg) {
  const n = intensity.length;
  if (nAvg <= 1 || n < 4) return intensity;
  const cap = Math.min(nAvg, Math.floor(n / 4));
  const out = [...intensity];
  let sumL = 0, sumR = 0;
  for (let i = 0; i < cap; i++) sumL += intensity[i];
  for (let i = n - cap; i < n; i++) sumR += intensity[i];
  const avgL = sumL / cap, avgR = sumR / cap;
  for (let i = 0; i < cap; i++) out[i] = avgL;
  for (let i = n - cap; i < n; i++) out[i] = avgR;
  return out;
}

// Shirley + Linear: a linear baseline plus a Shirley-like cumulative correction.
// Completely standalone — does not call shirleyBackground / smartBackground.
function shirleyLinearBackground(be, intensity, maxIter, nAvg) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);

  // 1. Averaged endpoints
  const cap = Math.min(nAvg || 1, Math.floor(n / 4)) || 1;
  let sL = 0, sR = 0;
  for (let i = 0; i < cap; i++) sL += intensity[i];
  for (let i = n - cap; i < n; i++) sR += intensity[i];
  const IL = sL / cap;   // left (high-BE) endpoint
  const IR = sR / cap;   // right (low-BE) endpoint

  // 2. Linear baseline between averaged endpoints
  const linear = new Array(n);
  for (let i = 0; i < n; i++) linear[i] = IL + (IR - IL) * i / (n - 1);

  // 3. Flatten: subtract linear baseline
  const flat = intensity.map((v, i) => v - linear[i]);

  // 4. Iterative Shirley-like correction on the flattened data.
  //    Step height = |IL - IR| (the endpoint difference drives the Shirley step).
  const stepH = Math.abs(IL - IR);
  if (stepH < 1e-12) return linear;   // endpoints equal → pure linear

  let bg = new Array(n).fill(0);      // Shirley correction term

  for (let iter = 0; iter < maxIter; iter++) {
    const newBg = new Array(n).fill(0);
    // Cumulative integral of (flattened signal - current bg) from right to left
    let totalInt = 0;
    for (let j = 0; j < n - 1; j++) {
      totalInt += ((Math.max(flat[j] - bg[j], 0) + Math.max(flat[j + 1] - bg[j + 1], 0)) / 2)
                  * Math.abs(be[j + 1] - be[j]);
    }
    if (totalInt <= 0) break;

    for (let i = 0; i < n; i++) {
      let sumRight = 0;
      for (let j = i; j < n - 1; j++) {
        sumRight += ((Math.max(flat[j] - bg[j], 0) + Math.max(flat[j + 1] - bg[j + 1], 0)) / 2)
                    * Math.abs(be[j + 1] - be[j]);
      }
      // Scale by step height, normalised by total integral
      newBg[i] = stepH * (sumRight / totalInt);
    }
    bg = newBg;
  }

  // 5. Combine: linear baseline + Shirley correction, clamped to data
  const result = new Array(n);
  for (let i = 0; i < n; i++) {
    result[i] = Math.min(linear[i] + bg[i], intensity[i]);
  }
  return result;
}

// Clear stored background so updatePlot recomputes it
function _invalidateBgCache() {
  if (state.fitResult) state.fitResult.bgIntensity = null;
}

// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
function _invalidateFittedY() {
  if (state.fitResult) state.fitResult.fittedY = null;
}

function _clampShirleyIter() {
  const el = document.getElementById('shirley-iter');
  let v = parseInt(el.value);
  if (isNaN(v)) return;
  if (v < 1) el.value = 1;
  else if (v > 50) el.value = 50;
}

// The background window. The user types two binding energies; the window
// is every grid point with lo <= BE <= hi, INCLUSIVE at both ends — the same
// rule getROIData uses for the ROI. This is the single definition shared by
// the preview (computeBackgroundCore) and both /api/fit request builders,
// which send end_idx = i1 + 1 because the backend slices Python-end-exclusive
// (unit 1c of docs/superpowers/plans/2026-09-02-background-architecture-
// sealed-fit-record.md, round-5 amendment — before 1c the builders sent the
// nearest grid index per bound and end_idx = i1, so the fit anchored one
// point inside the window the user drew).
// Returns inclusive indices { i0, i1 }. A blank/NaN bound, or fewer than two
// grid points inside the bounds, falls back to the full range.
// Contract notes (Codex round 1, both runs): (a) the window is the contiguous
// index span from the FIRST to the LAST in-range point — exact on a monotonic
// grid, which is what createTab guarantees (it sorts descending) and what
// every saved project written by this app carries; a hand-edited
// non-monotonic rawBE would make the span include out-of-window rows, and
// the preview and the request would still agree. (b) Indices are computed on
// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
// backend only ever applies the indices to that same-length, same-order
// session grid, so rounding cannot change which rows are used.
function _bgWindowIndices(be, bgStart, bgEnd) {
  const n = be.length;
  const full = { i0: 0, i1: n - 1 };
  const a = parseFloat(bgStart), b = parseFloat(bgEnd);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return full;
  const lo = Math.min(a, b), hi = Math.max(a, b);
  let i0 = -1, i1 = -1;
  for (let i = 0; i < n; i++) {
    if (be[i] >= lo && be[i] <= hi) { if (i0 < 0) i0 = i; i1 = i; }
  }
  if (i0 < 0 || i1 - i0 < 1) return full;
  return { i0, i1 };
}

// Pure-functional background computation. Takes explicit `settings`
// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
// endpointAvg) instead of reading from DOM. Used by stack-view render
// to reproduce a source tab's background from its persisted ui state.
// computeBackground() below is a thin DOM-reading wrapper for callers
// in the single-tab plot path.
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
  return computeBackgroundCore(be, intensity, {
    bgType:      document.getElementById('bg-type').value,
    shirleyIter: document.getElementById('shirley-iter').value,
    endpointAvg: document.getElementById('bg-endpoint-avg').value,
    bgStart:     document.getElementById('bg-start').value,
    bgEnd:       document.getElementById('bg-end').value,
  });
}

// ═══════════════════════════════════════════════════
// FILE PARSING
// ═══════════════════════════════════════════════════
function parseCSV(text) {
  const lines = text.trim().split('\n');
  const be = [], inten = [];
3176:        shirleyIter: '5', endpointAvg: NEW_TAB_ENDPOINT_AVG,
3209:      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
3396:        shirleyIter: document.getElementById('shirley-iter').value,
3463:        active.ui.shirleyIter = data.background.shirleyIter || '5';
3834:      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
3854:    set('shirley-iter', ui.shirleyIter);
4445:function smartBackground(be, intensity, maxIter, rawIntensity) {
4730:// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
4733:// computeBackground() below is a thin DOM-reading wrapper for callers
4735:function computeBackgroundCore(be, intensity, settings) {
4737:  const iter = parseInt(settings.shirleyIter) || 5;
4756:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
4785:function computeBackground(be, intensity) {
4786:  return computeBackgroundCore(be, intensity, {
4788:    shirleyIter: document.getElementById('shirley-iter').value,
5827:  const bgIntensity = computeBackground(be, inten);
7364:  const bgI2 = computeBackground(be2, inten2);
7609:  const bgI = computeBackground(corrBE, inten);
7835:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
7859:                  shirleyIter: v => parseInt(v), endpointAvg: v => parseInt(v) };
8146:  const bgIntensity = computeBackground(be, inten);
9262:    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
9268:  return computeBackgroundCore(be, inten, settings);
9819:                         : (be.length ? computeBackground(be, inten) : []);
10520:      shirleyIter: document.getElementById('shirley-iter').value,
10565:  const bgIntensity = computeBackground(be, inten);
11057:        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
11083:        shirleyIter: '5', roiMin: '', roiMax: '',
11246:  const bgIntensity = computeBackground(be, inten);
11307:  const bgArr   = computeBackground(be, inten);
12498:    const bgI = computeBackground(be, inten);
14514:  const shirleyIter = document.getElementById('shirley-iter');
14515:  if (shirleyIter) {
14516:    shirleyIter.disabled = !needsIter;
14517:    shirleyIter.style.opacity = needsIter ? '1' : '0.4';
16405:  // unfit-preview path (getROIData() + client-side computeBackground()),

exec
/bin/zsh -lc "cat docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md; git diff 895f323..HEAD -- templates/index.html; rg -n 'bg_func|shirley_background\\(|smart_background\\(|n_avg|isfinite' fitting.py | tail -80; rg -n 'shirley|smart|background' tests/js/*.test.js | head -110" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
# Task 4 — Background JS/Python twin parity (investigation only; NO fixes made)

Harness: the shipped JS functions were regex-extracted from
`templates/index.html` (main) and run in node against `fitting.py`'s twins on
IDENTICAL input arrays — 3 spectra (synthetic narrow C1s 101 pts, synthetic
wide U4f doublet 351 pts, the real U4f Scan_0 from the committed 1-GTA proj,
350 pts) × {ascending, descending} × n_avg {1, 10} × JS iteration {5 = UI
default, 50, 200}; 171 cases + non-uniform-grid and manual-anchor cases.
Calling conventions mirror `computeBackgroundCore` exactly. Scripts + full
row dump: scratchpad/task4/ (parity.py, js_bg_runner.mjs, parity_rows.json).
This isolates ALGORITHM divergence; the request-path window off-by-one is a
separate finding (Task 1 report) and applies ON TOP of everything below.

## Parity table (worst case per method × condition class; % of intensity span)

| method | condition | max divergence | verdict |
|---|---|---|---|
| **shirley_linear** | **descending grid (= all real data)**, any n_avg, any iter | **26.6–33.2% of span** (5077–6396 counts) | **DIVERGED — severe** |
| shirley_linear | ascending grid, iter ≥ 50 | 0.000 (exact) | agrees |
| **smart** | **n_avg = 10**, any direction, any iter | **0.72–1.04% of span** (46–171 counts), localized at the averaged edges | **DIVERGED — moderate** |
| smart | n_avg = 1 | ≤ 0.24% span (≤ 56 counts) — same mechanism as shirley below | diverged (small) |
| **shirley** | any direction, converged (iter ≥ 50) | 0.015–0.24% span (1–56 counts), mid-window | **DIVERGED — small but real** |
| smart_exp | all conditions | ≤ 0.008% span (≤ 1.8 counts) | agrees (within tol differences) |
| linear | uniform grids | 0 (exact) | agrees |
| linear | non-uniform grid | 0.034% span | latent divergence (index- vs BE-interpolation) |
| tougaard | all conditions | 0 (exact) | agrees — pinned twin confirmed locked in |
| manual (fit path) | uniform + non-uniform | 0 (exact vs np.interp) | agrees |

## Root causes — each PROVEN by exact reconstruction, not inferred

1. **shirley (and smart's base): the JS iteration does not clamp net signal
   at zero.** `shirleyBackground` integrates `(intensity − bg)` raw
   (index.html:4038); Python uses `max(y − B, 0)` (fitting.py:369). Noise
   channels below the background contribute NEGATIVE loss weight in JS. This
   is a different fixed point, not an iteration-count issue (identical at 50
   vs 200 iterations). Proof: re-implementing the JS loop in numpy and adding
   ONLY the clamp reproduces fitting.py to 0.000000 counts; without the clamp
   it reproduces the shipped JS to 0.000000 (verify_shirley_clamp.py).
   Python's clamped form is the Proctor–Sherwood-faithful one.

2. **smart at n_avg > 1: the two sides clamp against different data.**
   `computeBackgroundCore` hands the ENDPOINT-AVERAGED array to
   `smartBackground`, which clamps `min(shirley, averagedData)`; Python
   `smart_background` deliberately clamps against the RAW data (its
   docstring calls this out as the F3 design: "averaging only ever moves the
   background — never the reported net counts"). At the averaged edge caps
   (n/4-capped n_avg points) the clamp targets differ by the local
   noise-vs-mean gap. Proof: the clamp-target difference alone reproduces the
   full 161.33-count real-U4f divergence to 1e-12 (verify_smart_clamp.py).

3. **shirley_linear: the JS is order-SENSITIVE; Python is order-invariant.**
   The JS accumulates its Shirley-like correction integral in ARRAY order
   (`sumRight` toward the array end, index.html:4258-4262) and pins the
   step-height at whichever end of the ARRAY is index 0; Python normalizes to
   an ascending copy first, always placing the correction the same way in BE
   space. On ascending input they agree exactly; on DESCENDING input — which
   is every real acquisition — the correction lands on the OPPOSITE side of
   the window, and only the final min(data) clamp keeps the JS curve visually
   plausible ("under the data"), masking a 27–33%-of-span disagreement with
   the background the backend actually fit against.

4. **linear on non-uniform grids:** JS interpolates by index `i/(n−1)`
   (index.html:4135), Python by BE. Identical on uniform instrument grids;
   0.03% span on an alternating-step grid. Latent, low priority.

## Manual anchor background (item 2 — never-audited path)

- It DOES have a backend counterpart in the fit path: `runFit` sends
  `manual_bg = anchors as [x, y]` (index.html:6815) and `run_fit`
  interpolates them with `np.interp` over the full ROI (fitting.py:1038-1046).
  JS `manualAnchorBackground` (index.html:12477) is BE-based piecewise-linear
  with endpoint clamping — measured EXACT vs the backend interpolation on
  uniform and non-uniform grids. No structural mismatch in the fit path.
- Two real quirks: (a) `< 2 anchors` fallback differs — JS falls back to
  `linearBackground` (index-based), backend to `linear_background` (BE-based):
  same uniform-grid result, latent non-uniform divergence; (b)
  `/api/background` (`compute_background_only`) treats 'manual' as ZEROS —
  only `/api/fit` implements it. Nothing currently calls /api/background with
  'manual', so this is a landmine, not a live bug.
- The charge-correction frame problem for anchors is Task 6's report.

## bgSubtracted / display path (item 3)

Confirmed at code level (and numerically in the Task 1 reproduction): after a
backend fit, the drawn background curve (`plotBG`) and the Bkgrd-Sub view
baseline are the frozen **JS** background (`state.fitResult.bgIntensity` /
`.bgSubtracted`, index.html:7955-7963), while χ²/fittedY were computed
against the **Python** background. The residuals panel is internally
consistent (it diffs raw data against backend `fitted_y`), but the displayed
background ≠ the background actually subtracted in the fit, by the amounts in
the table above. For `shirley_linear` on real (descending) data that gap is
~30% of the span — very plausibly the kernel of the "backgrounds don't quite
work the way they should" feeling.

## Which side is likely canonical (NOT decided — for the morning)

- shirley / smart / smart_exp / tougaard: **Python** — Proctor-Sherwood-
  verified this session, order-invariant, and it is what the fit minimizes
  against. The JS signal-clamp and clamp-target gaps look like straight bugs
  to fix toward Python (small blast radius: display + saved bgIntensity).
- shirley_linear: Python is order-invariant and fit-side, so parity argues
  for porting Python's behavior to JS. BUT note both sides place a nonzero
  step at a window END (it is a heuristic hybrid, not literature Shirley), so
  if this method matters scientifically it deserves its own review rather
  than blind twin-alignment. Users on descending data have been LOOKING at
  the JS curve while FITTING against the Python one for as long as this
  method has existed.
- Blast radius of any JS-side alignment: display curves, saved
  bgIntensity/bgSubtracted arrays in .proj/.spec.json, the local-LM fallback
  fit (which fits against the JS bg), and every stack-view Path-B
  reconstruction. Backend fits, χ², refined params, and Quantify areas are
  NOT affected (they never touch the JS backgrounds).
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DEfRdBHI' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uRPTorlt' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 5d38496..b708de7 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4406,36 +4406,55 @@ function evalAllPeaks(beArray, peaks) {
 // BACKGROUND SUBTRACTION
 // ═══════════════════════════════════════════════════
 function shirleyBackground(be, intensity, maxIter) {
+  // fitting.shirley_background's iteration, step for step (unit 4, Codex
+  // round 1): the straight line between the endpoints as the first guess,
+  // the net signal clamped at zero (Proctor–Sherwood), the background KEPT
+  // when no net signal is left, and the same 1e-6 convergence stop. The
+  // clamp alone, on the old zero start and index-linear fallback, reached a
+  // different fixed point on data that dip below the baseline (33–58 % of the
+  // span on small cases). The array order does not matter: the cumulative
+  // integral runs to the array's end and the endpoints are the array's, which
+  // is fitting.py's ascending-copy form mirrored.
   const n = be.length;
   if (n < 2) return new Array(n).fill(0);
   const I0 = intensity[0], I1 = intensity[n - 1];
-  let bg = new Array(n).fill(0);
-
+  let bg = intensity.map((_, i) => I0 + (I1 - I0) * i / (n - 1));
   for (let iter = 0; iter < maxIter; iter++) {
-    const newBg = new Array(n).fill(0);
+    const cum = new Array(n).fill(0);            // cum[i] = ∫ net signal from point i to the array end
+    let sPrev = Math.max(intensity[n - 1] - bg[n - 1], 0);
+    for (let j = n - 2; j >= 0; j--) {
+      const sj = Math.max(intensity[j] - bg[j], 0);
+      cum[j] = cum[j + 1] + 0.5 * (sj + sPrev) * Math.abs(be[j + 1] - be[j]);
+      sPrev = sj;
+    }
+    const total = cum[0];
+    if (!(total > 0)) break;                     // no net signal left: keep the current background
+    let maxChange = 0;
+    const next = new Array(n);
     for (let i = 0; i < n; i++) {
-      let sumRight = 0;
-      for (let j = i; j < n - 1; j++) {
-        sumRight += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
-      }
-      let sumTotal = 0;
-      for (let j = 0; j < n - 1; j++) {
-        sumTotal += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
-      }
-      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
-      newBg[i] = I1 + (I0 - I1) * frac;
+      next[i] = I1 + (I0 - I1) * cum[i] / total;
+      const d = Math.abs(next[i] - bg[i]);
+      if (d > maxChange) maxChange = d;
     }
-    bg = newBg;
+    bg = next;
+    if (maxChange < 1e-6) break;                 // fitting.py's tolerance
   }
   return bg;
 }
 
-function smartBackground(be, intensity, maxIter) {
+function smartBackground(be, intensity, maxIter, rawIntensity) {
   // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
+  // The Shirley runs on `intensity` (the endpoint-averaged copy); the clamp is
+  // against the RAW data (`rawIntensity`, defaulting to `intensity`), as
+  // fitting.smart_background does: averaging only ever moves the background,
+  // never the reported net counts (Task 4 S5, unit 4 2026-09-27 — at an
+  // endpoint average of 10 the two sides differed by up to 1 % of the span at
+  // the averaged edges).
   const n = be.length;
   if (n < 2) return new Array(n).fill(0);
+  const raw = rawIntensity || intensity;
   const shir = shirleyBackground(be, intensity, maxIter);
-  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], intensity[i]);
+  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], raw[i]);
   return shir;
 }
 
@@ -4734,7 +4753,7 @@ function computeBackgroundCore(be, intensity, settings) {
   // Compute background on the sliced region — apply endpoint averaging for Shirley types
   let bgSub;
   if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
-  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
+  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
   else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
   else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
   else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
150:    result = np.where(np.isfinite(result), result, 0.0)
219:        core = np.where(np.isfinite(core), core, 0.0)
317:    return np.where(np.isfinite(result), result, 0.0)
324:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
325:    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
327:    if n_avg <= 1 or n < 4:
329:    cap = min(n_avg, n // 4)
338:def shirley_background(
343:    n_avg: int = 1,
350:    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
353:    sample propagates straight into the net area. n_avg=1 = raw endpoints =
369:    if n_avg > 1:
370:        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
402:def smart_background(
407:    n_avg: int = 1,
411:    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
418:    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
433:    n_avg: int = 1,
452:    cap = max(1, min(n_avg, n // 4))
489:    n_avg: int = 1,
493:    1. Average *n_avg* points at each endpoint.
513:    cap = max(1, min(n_avg, n // 4))
549:    n_avg: int = 1,
579:    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
581:    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
603:    if n_avg > 1:
604:        ya = _apply_endpoint_averaging(ya, n_avg)
1048:    xf, yf = xf[np.isfinite(xf)], yf[np.isfinite(yf)]
1058:        open_min, open_max = not np.isfinite(par.min), not np.isfinite(par.max)
1317:        both = np.isfinite(lo) and np.isfinite(hi)
1321:            if np.isfinite(lo):
1323:            if np.isfinite(hi):
1391:        if not trial.success or trial.redchi is None or not np.isfinite(trial.redchi):
1447:    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
1459:    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
1516:    if not np.isfinite(chi2_without):
1653:        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
1655:        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
1657:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
1659:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
1661:        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
1756:    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
1805:                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
1806:                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')
1844:                    if np.isfinite(par.min):
1846:                    if np.isfinite(par.max):
1962:                    "min": float(par.min) if np.isfinite(par.min) and "min" not in search_box.get(pname, {}) else None,
1963:                    "max": float(par.max) if np.isfinite(par.max) and "max" not in search_box.get(pname, {}) else None,
2071:        bg = shirley_background(x, y, n_avg=endpoint_avg)
2073:        bg = smart_background(x, y, n_avg=endpoint_avg)
2075:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
2077:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
2079:        bg = tougaard_background(x, y, n_avg=endpoint_avg)
tests/js/background_parity.test.js:1:// Unit 4 (2026-09-27): the page's background twins against fitting.py — the
tests/js/background_parity.test.js:4:// background-twin-parity.md) measured the gaps and proved their causes;
tests/js/background_parity.test.js:6://   S4 shirley: the JS integrated the raw net signal, fitting.py max(y−B, 0)
tests/js/background_parity.test.js:8://   S5 smart at endpoint averaging > 1: the JS clamped against the averaged
tests/js/background_parity.test.js:10:// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
tests/js/background_parity.test.js:18:// tests/js/background_parity_backend.py.
tests/js/background_parity.test.js:45:const BRIDGE = path.join(__dirname, 'background_parity_backend.py');
tests/js/background_parity.test.js:49:  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
tests/js/background_parity.test.js:55:  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });
tests/js/background_parity.test.js:75:for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
tests/js/background_parity.test.js:77:    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
tests/js/background_parity.test.js:93:test('below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)', () => {
tests/js/background_parity.test.js:94:  for (const method of ['shirley', 'smart']) {
tests/js/background_parity.test.js:98:        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '1', bgStart: '', bgEnd: '' });
tests/js/background_parity.test.js:113:test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
tests/js/background_parity.test.js:114:  const rows = compare('shirley_linear', 1);
tests/js/background_parity.test.js:119:  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
tests/js/stale_statistics.test.js:339:  const ui = { bgType: 'shirley', bgStart: '295', bgEnd: '280', shirleyIter: '10', endpointAvg: '3', roiMin: '280', roiMax: '295' };
tests/js/stale_statistics.test.js:343:  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, bgType: 'linear' }, 0, [])), 'a background change');
tests/js/stale_statistics.test.js:348:    ['endpointAvg', '30', '3e1', false],     // Number('3e1') = 30, parseInt('3e1') = 3: a different background
tests/js/stale_statistics.test.js:350:    ['shirleyIter', '5', '5.0', true],       // parseInt: 5 either way
tests/js/stale_statistics.test.js:351:    ['shirleyIter', '5', '5.9', true],       // parseInt reads 5 — the same fit
tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
tests/js/tougaard_twin.test.js:56:  // pedestal has no loss intensity to model and yields a flat background with
tests/js/tougaard_twin.test.js:74:test('ascending and descending BE input give the identical background', () => {
tests/js/tougaard_twin.test.js:85:test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
tests/js/tougaard_twin.test.js:93:  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
tests/js/tougaard_twin.test.js:94:  // background to dive to zero regardless of the data.
tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:148:// (fitting.py run_fit / compute_background_only both do
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:153:  // Stubs for background types this test never routes to; the eval'd
tests/js/tougaard_twin.test.js:156:  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
tests/js/tougaard_twin.test.js:157:  const smartBackground = () => { throw new Error('unexpected route: smart'); };
tests/js/tougaard_twin.test.js:158:  const smartExperimentalBackground = () => { throw new Error('unexpected route: smart_exp'); };
tests/js/tougaard_twin.test.js:159:  const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:186:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/scattered_starts.test.js:40:  const ui = { bgType: 'shirley', bgStart: '281.0', bgEnd: '294.0', shirleyIter: '5', endpointAvg: '3', roiMin: '280', roiMax: '295' };
tests/js/scattered_starts.test.js:168:  ['the background type changed', (ps, env) => { env.ui.bgType = 'linear'; return ps; }],
tests/js/scattered_starts.test.js:169:  ['the background window moved', (ps, env) => { env.ui.bgEnd = '292.5'; return ps; }],
tests/js/lineshape_roundtrip.test.js:13:// on the server (fitting.run_fit, no background, Trust-Region), apply the
tests/js/local_lm_descent.test.js:39:  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
tests/js/local_lm_descent.test.js:41:  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
tests/js/endpoint_avg_default.test.js:7:// and stack Path B / re-render reconstruct the background from that value.
tests/js/bg_window_indices.test.js:2:// design, docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md,
tests/js/bg_window_indices.test.js:5:// The user types two binding energies; the preview background, the fit
tests/js/bg_window_indices.test.js:100:    'shirleyBackground', 'smartBackground', 'smartExperimentalBackground',
tests/js/bg_window_indices.test.js:101:    'shirleyLinearBackground', 'tougaardBackground', '_applyEndpointAveraging',
tests/js/bg_window_indices.test.js:104:  const unused = () => { throw new Error('unexpected background type call'); };
tests/js/bg_window_indices.test.js:110:    const out = core(be, inten, { bgType: 'linear', shirleyIter: '5', endpointAvg: '1', bgStart: s, bgEnd: e });
tests/js/batch_propagation.test.js:9:    bgType: 'shirley', bgStart: '700', bgEnd: '740', shirleyIter: '5',
tests/js/batch_propagation.test.js:40:// --- no regression: background propagation behaves exactly as before ---
tests/js/batch_propagation.test.js:41:test('background fields still propagate from source (no regression)', () => {
tests/js/batch_propagation.test.js:42:  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
tests/js/batch_propagation.test.js:43:  const tgt = ui({ bgType: 'shirley', bgStart: '700', bgEnd: '740', shirleyIter: '5' });
tests/js/batch_propagation.test.js:48:  assert.strictEqual(out.shirleyIter, '9');
tests/js/batch_propagation.test.js:66:  // endpoint averaging IS background-affecting and propagates with the
tests/js/batch_propagation.test.js:67:  // background (sealed-fit-record memo R3-B5; Codex 2026-09-08 both runs)
tests/js/batch_propagation.test.js:70:  const propagated = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/background_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 1127ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
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
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
# node:child_process:955
#     throw err;
#     ^
# Error: Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
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
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
#     at genericNodeError (node:internal/errors:983:15)
#     at wrappedFn (node:internal/errors:537:14)
#     at checkExecSyncError (node:child_process:916:11)
#     at execFileSync (node:child_process:952:15)
#     at py (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:46:30)
#     at Object.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:57:15)
#     at Module._compile (node:internal/modules/cjs/loader:1705:14)
#     at Object..js (node:internal/modules/cjs/loader:1838:10)
#     at Module.load (node:internal/modules/cjs/loader:1441:32)
#     at Function._load (node:internal/modules/cjs/loader:1263:12) {
#   status: 1,
#   signal: null,
#   output: [
#     null,
#     '',
#     'Traceback (most recent call last):\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#       '    import fitting  \# noqa: E402\\n' +
#       '    ^^^^^^^^^^^^^^\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#       '    from lmfit import Model, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#       '    from .confidence import conf_interval, conf_interval2d\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#       '    from .minimizer import MinimizerException\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#       '    from .parameter import Parameter, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#       '    from .jsonutils import decode4js, encode4js\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#       '    import dill\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#       '    from .session import (\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#       '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#       '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#       '    return _os.fsdecode(_gettempdir())\\n' +
#       '                        ^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#       '    tempdir = _get_default_tempdir()\\n' +
#       '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#       '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#       "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
#   ],
#   pid: 76104,
#   stdout: '',
#   stderr: 'Traceback (most recent call last):\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#     '    import fitting  \# noqa: E402\\n' +
#     '    ^^^^^^^^^^^^^^\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#     '    from lmfit import Model, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#     '    from .confidence import conf_interval, conf_interval2d\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#     '    from .minimizer import MinimizerException\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#     '    from .parameter import Parameter, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#     '    from .jsonutils import decode4js, encode4js\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#     '    import dill\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#     '    from .session import (\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#     '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#     '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#     '    return _os.fsdecode(_gettempdir())\\n' +
#     '                        ^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#     '    tempdir = _get_default_tempdir()\\n' +
#     '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#     '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#     "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
# }
# Node.js v22.22.2
# Subtest: tests/js/background_parity.test.js
not ok 1 - tests/js/background_parity.test.js
  ---
  duration_ms: 1173.467046
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:1:1'
  failureType: 'testCodeFailure'
  exitCode: 1
  signal: ~
  error: 'test failed'
  code: 'ERR_TEST_FAILURE'
  ...
1..1
# tests 1
# suites 0
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 1182.634405

codex
The new tests cover the round-1 reproducers, and both `smart_exp` and `shirley_linear` use independent iterations. I’m now probing finite-precision edge cases: a tiny positive residual above the initial line could send JS and Python down different paths.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/background_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "sed -n '4723,4785p' templates/index.html; sed -n '9280,9380p' templates/index.html; sed -n '1615,1685p' fitting.py; rg -n 'shirleyIter|computeBackgroundCore\\(|smartBackground\\(' templates/index.html | head -65; sed -n '3980,4007p' docs/autofit/codex/background_twins_verdict_runA.md; sed -n '4680,4706p' docs/autofit/codex/background_twins_verdict_runB.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
    if (be[i] >= lo && be[i] <= hi) { if (i0 < 0) i0 = i; i1 = i; }
  }
  if (i0 < 0 || i1 - i0 < 1) return full;
  return { i0, i1 };
}

// Pure-functional background computation. Takes explicit `settings`
// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
// endpointAvg) instead of reading from DOM. Used by stack-view render
// to reproduce a source tab's background from its persisted ui state.
// computeBackground() below is a thin DOM-reading wrapper for callers
// in the single-tab plot path.
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
//         ccShift, matching single-tab behavior.
//   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
//       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
//   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
//       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
//       bg via _computeBackgroundForSource(be, inten, src.ui).
//       Live ccShift (deliberate asymmetry vs A/A2).
//
// Returns empty arrays if source isn't available or has no fit.
// Align src.rawIntensity to a fit-time `be` array (Path A/A2). fr.be is
// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
// we can find the matching window in current rawBE by locating the
// index where (rawBE - shift) is closest to be[0]. Returns rawIntensity
// slice of length matching `be` (or shorter if data runs out).
function _alignRawToFitBe(src, be) {
  if (!Array.isArray(src.rawBE) || !Array.isArray(src.rawIntensity)
      || src.rawBE.length === 0 || !be || be.length === 0) return [];
  const shift = src.ccShift || 0;
  const target = be[0];
  let i0 = 0;
  let minDiff = Math.abs((src.rawBE[0] - shift) - target);
  for (let i = 1; i < src.rawBE.length; i++) {
    const d = Math.abs((src.rawBE[i] - shift) - target);
    if (d < minDiff) { minDiff = d; i0 = i; }
    else if (i0 > 0) break;  // rawBE is monotonic; past the closest match.
  }
  const len = Math.min(be.length, src.rawBE.length - i0);
  return src.rawIntensity.slice(i0, i0 + len);
}

function _buildEntryRenderData(entry) {
  const src = tabManager._getTab(entry.sourceTabId);
  if (!src || !Array.isArray(src.rawBE) || src.rawBE.length < 2) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const peaks = Array.isArray(src.peaks) ? src.peaks : [];
  const fr = src.fitResult;
  if (!fr || peaks.length === 0) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const shift = src.ccShift || 0;

  // be + bg + rawY
  let be, bg, rawY;
  if (Array.isArray(fr.be) && fr.be.length >= 2
      && Array.isArray(fr.bgIntensity)
      && fr.bgIntensity.length === fr.be.length) {
    // Path A/A2: fit-time be + bg both present (frozen).
    be = fr.be.slice();
    bg = fr.bgIntensity.slice();
    rawY = _alignRawToFitBe(src, be);
  } else {
    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
    // recompute bg from raw via source's persisted bg settings.
    const corrBE = src.rawBE.map(b => b - shift);
    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
    let i0 = 0, i1 = corrBE.length - 1;
    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
      const lo = Math.min(roiMinV, roiMaxV);
      const hi = Math.max(roiMinV, roiMaxV);
      // corrBE is descending (highest BE first); locate ROI bounds.
      while (i0 < corrBE.length && corrBE[i0] > hi) i0++;
      while (i1 >= 0 && corrBE[i1] < lo) i1--;
      if (i1 < i0) { i0 = 0; i1 = corrBE.length - 1; }
    }
    be = corrBE.slice(i0, i1 + 1);
    rawY = src.rawIntensity.slice(i0, i1 + 1);
    bg = _computeBackgroundForSource(be, rawY, src.ui);
  }

  // Envelope (raw-level)
  let fittedY;
  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length && _statsRecordState(src) !== 'stale') {
    // Path A: backend fittedY directly (already raw-level). Never a stale
    // result's curve (F1: judged against the SOURCE record's key).
    fittedY = fr.fittedY.slice();
  } else {
    // Path A2/B: compose envelope from peaks + bg.
    const model = evalAllPeaks(be, peaks);
    fittedY = model.map((v, i) => v + bg[i]);
  }

  // Per-peak curves. peakOnly = pure peak shape (bg-subtracted level);
  // y = peakOnly + bg (raw level). Both kept so Bkgrd Sub view can
  // pick the appropriate one without recomputing.
  const peakCurves = peaks.map(p => {
    const peakOnly = evalPeakArray(be, p);
    return { peak: p, peakOnly, y: peakOnly.map((v, i) => v + bg[i]) };
  });

  return { be, bg, rawY, fittedY, peaks: peakCurves };
}

// Cached wrapper around _buildEntryRenderData. Stored on the entry as
// entry._renderDataCache. Slider drags and other in-place updates hit
// the cache; _renderStackChart clears all entry caches before rebuild,
// which is the only path that runs when source-tab state changes
// (peak edits, ccShift edits, re-fits all happen while user is on the
// source tab — they return to the stack via activateTab → updatePlot →
// _renderStackChart, picking up fresh data).
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
3176:        shirleyIter: '5', endpointAvg: NEW_TAB_ENDPOINT_AVG,
3209:      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
3396:        shirleyIter: document.getElementById('shirley-iter').value,
3463:        active.ui.shirleyIter = data.background.shirleyIter || '5';
3834:      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
3854:    set('shirley-iter', ui.shirleyIter);
4445:function smartBackground(be, intensity, maxIter, rawIntensity) {
4730:// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
4735:function computeBackgroundCore(be, intensity, settings) {
4737:  const iter = parseInt(settings.shirleyIter) || 5;
4756:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
4786:  return computeBackgroundCore(be, intensity, {
4788:    shirleyIter: document.getElementById('shirley-iter').value,
7835:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
7859:                  shirleyIter: v => parseInt(v), endpointAvg: v => parseInt(v) };
9262:    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
9268:  return computeBackgroundCore(be, inten, settings);
10520:      shirleyIter: document.getElementById('shirley-iter').value,
11057:        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
11083:        shirleyIter: '5', roiMin: '', roiMax: '',
14514:  const shirleyIter = document.getElementById('shirley-iter');
14515:  if (shirleyIter) {
14516:    shirleyIter.disabled = !needsIter;
14517:    shirleyIter.style.opacity = needsIter ? '1' : '0.4';
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 9238.099171

codex
1. **MAJOR — The clamp introduces a different converged Shirley result on below-baseline data.** [templates/index.html:4424](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4424)

   Reproducer: `be=[0,1,2,3,4]`, `intensity=[10,5,5,17,20]`, endpoint averaging `1`.

   | Method | Python / F3 JS | New JS |
   |---|---|---|
   | Shirley | `[10,12.5,15,17.5,20]` | `[10,10,10,15,20]` |
   | Smart | `[10,5,5,17,20]` | `[10,5,5,15,20]` |

   Python starts from the linear baseline, finds zero positive net signal, and keeps that baseline. JS starts from zeros; adding the clamp sends it to another fixed point. Confirmed in both directions at **5, 50, 200, 201 and 1,000 iterations**—this exceeds the deferred iteration-count gap. Shirley differs by **33.3% of the intensity span**; smart creates positive net counts where Python has none.

   This reaches display, frozen backgrounds, saves, and local/Batch Fit inputs. Align initialization and zero-total handling with Python and add this regression case; the current peak-rich fixtures miss it.

2. **MINOR — The new documentation overstates parity for linear backgrounds.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748)

   On `be=[0,1,3,6,10]`, `intensity=[10,5,5,17,20]`, JS linear returns `[10,12.5,15,17.5,20]`; Python returns `[10,11,13,16,20]`. This is the pre-existing index-versus-energy interpolation gap already recorded in Task 4, but the new blanket parity claim omits it. Qualify the claim to the tested cases and retain this known gap; no linear implementation change is required for this unit.

Validation: all **12 parity tests pass**; substituting F3’s page produces exactly the **four expected failures**. Another **72 adjacent tests pass**. Python-backed runs required an in-memory temporary-directory workaround for the read-only sandbox. The real scan loads, smart’s sole production caller passes the raw slice, and the `shirley_linear` divergence/de-listing assertions pass. No files changed.

**VERDICT: NO-GO.**
tokens used
/Users/skyefortier/.matplotlib is not a writable directory
{"case":"nonuniform linear","js":[10,25,40],"python":[10,20,40]}
/Users/skyefortier/.matplotlib is not a writable directory
{"case":"nonuniform smart regression","js":[6,6,7.181818181818182,19],"old":[6,7,13,19],"python":[6,7,13,19]}

codex
1. **MAJOR — The new clamp interacts with the existing initialization/fallback to produce persistent cycles.** [templates/index.html:4428](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4428), particularly the fallback at line 4430.

   Reproducer: descending `be=[3.5,1.1,1,0]`, `intensity=[6,7,13,19]`, endpoint averaging `1`, iterations `200`.

   | Background | Python and F3 JS | New JS |
   |---|---|---|
   | Shirley | `[6,10.333333,14.666667,19]` | `[6,6,7.181818,19]` |
   | Smart | `[6,7,13,19]` | `[6,6,7.181818,19]` |

   Shirley’s error is **57.6% of the intensity span**, introduced by this change. Both outputs remain wrong at 2,000 iterations. Python starts from a linear background and retains it when the integral vanishes; JS starts from zeros and can enter a cycle involving its linear fallback.

   This also occurs on uniform grids: `be=[3,2,1,0]`, `intensity=[100,107,120,127]` gives Shirley `[100,100,113.5,127]` at both 5 and 200 iterations, versus Python `[100,107,120.5,127]`. Increasing the iteration count does not resolve it. Add these cases and resolve the initialization/zero-integral interaction before shipping. Display, frozen backgrounds, local fitting and stack reconstruction inherit the error.

2. **MINOR — The new documentation overstates the parity guarantee.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748).

   It claims parity for `linear` without preserving Task 4’s known non-uniform-grid exception. With `be=[0,1,3]`, `intensity=[10,20,40]`, JS returns `[10,25,40]`; Python returns `[10,20,40]`: **16.7% of span**. This implementation gap predates the branch; qualify the new claim rather than expanding this unit to fix linear.

Verification: all 12 new tests pass; replaying them against F3 produces exactly the four promised Shirley/smart failures. The real scan loads, the bridge uses the correct backend functions, and the documented measurements reproduce. The smart caller passes the raw slice correctly; `smart_exp` and `shirley_linear` remain untouched. The divergence/de-listing pin is effective. The 76 selected related tests also pass after handling the sandbox’s Python temporary-directory import issue in memory. No files changed.

**VERDICT: NO-GO**
tokens used

 exited 1 in 1403ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
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
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
# node:child_process:955
#     throw err;
#     ^
# Error: Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
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
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
#     at genericNodeError (node:internal/errors:983:15)
#     at wrappedFn (node:internal/errors:537:14)
#     at checkExecSyncError (node:child_process:916:11)
#     at execFileSync (node:child_process:952:15)
#     at py (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:46:30)
#     at Object.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:57:15)
#     at Module._compile (node:internal/modules/cjs/loader:1705:14)
#     at Object..js (node:internal/modules/cjs/loader:1838:10)
#     at Module.load (node:internal/modules/cjs/loader:1441:32)
#     at Function._load (node:internal/modules/cjs/loader:1263:12) {
#   status: 1,
#   signal: null,
#   output: [
#     null,
#     '',
#     'Traceback (most recent call last):\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#       '    import fitting  \# noqa: E402\\n' +
#       '    ^^^^^^^^^^^^^^\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#       '    from lmfit import Model, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#       '    from .confidence import conf_interval, conf_interval2d\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#       '    from .minimizer import MinimizerException\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#       '    from .parameter import Parameter, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#       '    from .jsonutils import decode4js, encode4js\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#       '    import dill\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#       '    from .session import (\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#       '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#       '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#       '    return _os.fsdecode(_gettempdir())\\n' +
#       '                        ^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#       '    tempdir = _get_default_tempdir()\\n' +
#       '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#       '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#       "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
#   ],
#   pid: 76205,
#   stdout: '',
#   stderr: 'Traceback (most recent call last):\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#     '    import fitting  \# noqa: E402\\n' +
#     '    ^^^^^^^^^^^^^^\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#     '    from lmfit import Model, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#     '    from .confidence import conf_interval, conf_interval2d\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#     '    from .minimizer import MinimizerException\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#     '    from .parameter import Parameter, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#     '    from .jsonutils import decode4js, encode4js\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#     '    import dill\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#     '    from .session import (\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#     '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#     '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#     '    return _os.fsdecode(_gettempdir())\\n' +
#     '                        ^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#     '    tempdir = _get_default_tempdir()\\n' +
#     '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#     '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#     "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
# }
# Node.js v22.22.2
# Subtest: tests/js/background_parity.test.js
not ok 1 - tests/js/background_parity.test.js
  ---
  duration_ms: 1425.64508
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:1:1'
  failureType: 'testCodeFailure'
  exitCode: 1
  signal: ~
  error: 'test failed'
  code: 'ERR_TEST_FAILURE'
  ...
1..1
# tests 1
# suites 0
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 1436.527059

exec
/bin/zsh -lc "rg -n 'tempfile.tempdir|TemporaryDirectory|MPLCONFIGDIR|runpy|in-memory|Module._|_compile' docs/autofit/codex/background_twins_verdict_runA.md | head -35; rg -n 'shirley-iter|isFinite\\(|Number.isFinite|rawIntensity.*filter' templates/index.html | head -70; head -65 fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
1470:#     at Module._compile (node:internal/modules/cjs/loader:1705:14)
1979:The smart call site correctly passes the raw slice, and I found no other production callers of `smartBackground`. The bridge matches the backend’s anchor-window calls. The test run hit a Python dependency’s temporary-directory probe in this read-only sandbox; I’m checking whether an in-memory workaround will let it run. I’m also probing Shirley’s zero-signal behavior.
1983:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
2004:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
2030:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
2499:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
2813:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
3743:cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''local_lm_server_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
4004:Validation: all **12 parity tests pass**; substituting F3’s page produces exactly the **four expected failures**. Another **72 adjacent tests pass**. Python-backed runs required an in-memory temporary-directory workaround for the read-only sandbox. The real scan loads, smart’s sole production caller passes the raw slice, and the `shirley_linear` divergence/de-listing assertions pass. No files changed.
4026:Validation: all **12 parity tests pass**; substituting F3’s page produces exactly the **four expected failures**. Another **72 adjacent tests pass**. Python-backed runs required an in-memory temporary-directory workaround for the read-only sandbox. The real scan loads, smart’s sole production caller passes the raw slice, and the `shirley_linear` divergence/de-listing assertions pass. No files changed.
2045:                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
2641:      if (typeof v === 'number' && isFinite(v) && v > maxY) maxY = v;
2644:  if (!isFinite(maxY) || maxY <= 0) return { max: 100, step: 1 };
3396:        shirleyIter: document.getElementById('shirley-iter').value,
3834:      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
3854:    set('shirley-iter', ui.shirleyIter);
3875:      const si = document.getElementById('shirley-iter');
4102:  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
4112:  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
4315:  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
4366:  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
4688:  const el = document.getElementById('shirley-iter');
4719:  if (!Number.isFinite(a) || !Number.isFinite(b)) return full;
4788:    shirleyIter: document.getElementById('shirley-iter').value,
4806:    if (isFinite(x) && isFinite(y)) { be.push(x); inten.push(y); }
4819:    if (isFinite(x) && isFinite(y)) { be.push(x); inten.push(y); }
4833:    if (v > 0 && v < 2000 && isFinite(v)) {
4835:      if (next > 0 && next < 1e9 && isFinite(next)) {
4866:      if (isFinite(v)) nums.push(v);
5143:  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
5153:  const past = (Number.isFinite(lo) && lo < dMin - step) || (Number.isFinite(hi) && hi > dMax + step);
5176:  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
5389:    if (Number.isFinite(w)) peak[newWF] = w;
5452:          if (typeof v === 'number' && isFinite(v) && v > _maxY) _maxY = v;
6005:  if (!isFinite(r) || r < 0.01) r = 0.01;
6385:        <input type="number" value="${Number.isFinite(p.caM) ? +p.caM.toFixed(2) : 50}" step="0.1" min="0" max="499"
6504:    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
6505:    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
6510:    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
6511:    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
6514:    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
6515:    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
6520:    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
6521:    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
6522:    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
6528:    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
6529:    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
6530:    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
6603:// `shirley-iter` is gated when bg-type doesn't need iteration.
6694:    // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
7096:    if (!Number.isFinite(a) || a < 0) continue;
7193:    if (!Number.isFinite(counts[i]) || !Number.isFinite(fitted[i]) || !Number.isFinite(comp[i])) continue;
7199:  return { f: Number.isFinite(f) ? f : null, delta_chi2: delta, supported: delta > 0 && (withC === 0 || f >= _SUPPORT_MIN_F) };
7209:  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
7282:  if (!Number.isFinite(amp) || amp <= 0) return false;
7290:    if (!Number.isFinite(counts[i]) || !Number.isFinite(fit[i]) || !Number.isFinite(comp[i])) continue;
7300:  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
7309:  if (!gPeak || !Number.isFinite(gPeak.center)) {
7347:  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);
7565:      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
7612:  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
7676:      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
7677:      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
7678:      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
7679:      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
7785:    const shift = Number.isFinite(tab.ccShift) ? tab.ccShift : 0;
7789:    if (Number.isFinite(a) && Number.isFinite(b)) {
7799:  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
7869:      return Number.isFinite(n) ? String(n) : v;
8440:  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
8444:  } else if (fr && Number.isFinite(fr.chiReduced)) {
8474:  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
8484:      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
8516:        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
8517:        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
8518:        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
8521:        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
8522:        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
8533:  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
8577:      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv

Backgrounds
-----------
  shirley         – iterative Shirley (Proctor & Sherwood 1982)
  linear          – straight‑line between endpoints
  none            – flat zero

Spin‑orbit constraints are handled via lmfit parameter expressions.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
import time
import warnings
from typing import Any

import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
# ─────────────────────────────────────────────────────────────────────────────

_LN2 = np.log(2.0)
_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447


def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Gaussian; amplitude is the peak maximum value."""
    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)


def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Lorentzian; amplitude is the peak maximum value."""
    hwhm = fwhm / 2.0
    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)


def _pseudo_voigt_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    gl_ratio: float,
) -> np.ndarray:

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''child_process'\\'');const orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){ if(args?.[0]?.endsWith('\\''_backend.py'\\'')) return orig(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return orig(file,args,opts);};
require('\\''./tests/js/background_parity.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting, numpy as np, json, subprocess
rng=np.random.default_rng(928)
cases=[]
for n in range(2,13):
 for k in range(120):
  a,b=rng.integers(1,1000,2)/10
  y=np.linspace(a,b,n)
  if k%2 and n>2: y[1:-1]-=rng.integers(0,3,n-2)
  for desc in [False,True]:
   x=np.arange(n,dtype=float)
   yy=y.copy()
   if desc: x,yy=x[::-1],yy[::-1]
   cases.append(dict(x=x.tolist(),y=yy.tolist()))
code=\"\"\"const fs=require('\\''fs'\\'');const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');const f=h.slice(h.indexOf('\\''function shirleyBackground('\\''),h.indexOf('\\''function smartBackground('\\''));const fn=new Function(f+'\\'';return shirleyBackground'\\'')();const cases=JSON.parse(fs.readFileSync(0,'\\''utf8'\\''));console.log(JSON.stringify(cases.map(c=>fn(c.x,c.y,200))));\"\"\"
out=json.loads(subprocess.check_output(['\\''node'\\'','\\''-e'\\'',code],input=json.dumps(cases),text=True))
found=[]
for c,js in zip(cases,out):
 py=fitting.shirley_background(np.array(c['\\''x'\\'']),np.array(c['\\''y'\\'']))
 err=np.max(np.abs(py-js))/max(np.ptp(c['\\''y'\\'']),1e-9)
 if err>1e-6: found.append((err,c,js,py.tolist()))
print('\\''TOTAL'\\'',len(cases),'\\''FAIL'\\'',len(found))
for err,c,js,py in sorted(found,key=lambda r:-r[0])[:12]: print(json.dumps(dict(err=err,**c,js=js,py=py)))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1958ms:
/Users/skyefortier/.matplotlib is not a writable directory
TOTAL 2640 FAIL 490
{"err": 0.9090909090909094, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [22.7, 21.19090909090909, 19.68181818181818, 18.172727272727272, 16.663636363636364, 15.154545454545453, 13.645454545454545, 12.136363636363635, 10.627272727272725, 9.118181818181816, 7.609090909090906, 6.1], "js": [22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 22.700000000000003, 6.1], "py": [22.7, 21.19090909090909, 19.68181818181818, 18.172727272727272, 16.663636363636364, 15.154545454545453, 13.645454545454545, 12.136363636363635, 10.627272727272725, 9.118181818181816, 7.609090909090906, 6.1]}
{"err": 0.9090909090909094, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [24.8, 22.28181818181818, 19.763636363636365, 20.245454545454546, 18.727272727272727, 15.209090909090907, 14.69090909090909, 14.172727272727272, 11.654545454545453, 9.136363636363633, 9.618181818181816, 8.1], "js": [24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 24.800000000000004, 8.1], "py": [24.8, 23.28181818181818, 21.763636363636365, 20.245454545454546, 18.727272727272727, 17.209090909090907, 15.69090909090909, 14.172727272727272, 12.654545454545453, 11.136363636363633, 9.618181818181816, 8.1]}
{"err": 0.9090909090909092, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [26.3, 30.581818181818182, 34.86363636363637, 39.14545454545455, 43.42727272727273, 47.70909090909091, 51.9909090909091, 56.27272727272728, 60.55454545454546, 64.83636363636364, 69.11818181818182, 73.4], "js": [26.299999999999997, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4, 73.4], "py": [26.3, 30.581818181818182, 34.86363636363637, 39.14545454545455, 43.42727272727273, 47.70909090909091, 51.9909090909091, 56.27272727272728, 60.55454545454546, 64.83636363636364, 69.11818181818182, 73.4]}
{"err": 0.9090909090909092, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [66.5, 61.30909090909091, 54.11818181818182, 50.92727272727272, 45.736363636363635, 38.54545454545455, 34.35454545454545, 28.163636363636357, 22.97272727272727, 17.78181818181818, 13.590909090909086, 9.4], "js": [66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 66.5, 9.4], "py": [66.5, 61.30909090909091, 56.11818181818182, 50.92727272727272, 45.736363636363635, 40.54545454545455, 35.35454545454545, 30.163636363636357, 24.97272727272727, 19.78181818181818, 14.590909090909086, 9.4]}
{"err": 0.9090909090909092, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [12.8, 11.918181818181818, 11.036363636363637, 10.154545454545454, 9.272727272727273, 8.39090909090909, 7.509090909090909, 6.627272727272727, 5.745454545454545, 4.863636363636363, 3.9818181818181806, 3.1], "js": [12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 12.8, 3.1], "py": [12.8, 11.918181818181818, 11.036363636363637, 10.154545454545454, 9.272727272727273, 8.39090909090909, 7.509090909090909, 6.627272727272727, 5.745454545454545, 4.863636363636363, 3.9818181818181806, 3.1]}
{"err": 0.9090909090909092, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [95.3, 88.05454545454545, 80.80909090909091, 73.56363636363636, 66.31818181818181, 59.07272727272726, 51.82727272727272, 44.58181818181818, 37.33636363636363, 30.09090909090908, 22.84545454545453, 15.6], "js": [95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 95.3, 15.6], "py": [95.3, 88.05454545454545, 80.80909090909091, 73.56363636363636, 66.31818181818181, 59.07272727272726, 51.82727272727272, 44.58181818181818, 37.33636363636363, 30.09090909090908, 22.84545454545453, 15.6]}
{"err": 0.9090909090909092, "x": [11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0], "y": [99.7, 89.25454545454545, 80.8090909090909, 72.36363636363636, 64.91818181818182, 56.47272727272727, 47.027272727272724, 38.58181818181818, 32.13636363636363, 22.69090909090909, 13.245454545454546, 6.8], "js": [99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 99.70000000000002, 6.8], "py": [99.7, 91.25454545454545, 82.8090909090909, 74.36363636363636, 65.91818181818182, 57.47272727272727, 49.027272727272724, 40.58181818181818, 32.13636363636363, 23.69090909090909, 15.245454545454546, 6.8]}
{"err": 0.9090909090909091, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [66.9, 61.07272727272728, 55.24545454545455, 49.41818181818182, 43.59090909090909, 37.763636363636365, 31.936363636363637, 26.10909090909091, 20.28181818181818, 14.454545454545453, 8.627272727272725, 2.8], "js": [66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 66.9, 2.8], "py": [66.9, 61.07272727272728, 55.24545454545455, 49.41818181818182, 43.59090909090909, 37.763636363636365, 31.936363636363637, 26.10909090909091, 20.28181818181818, 14.454545454545453, 8.627272727272725, 2.8]}
{"err": 0.9090909090909091, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [73.7, 66.26363636363637, 61.82727272727273, 55.39090909090909, 49.95454545454545, 46.518181818181816, 39.081818181818186, 34.64545454545455, 28.20909090909091, 23.772727272727273, 18.336363636363636, 13.9], "js": [73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 73.7, 13.9], "py": [73.7, 68.26363636363637, 62.82727272727273, 57.39090909090909, 51.95454545454545, 46.518181818181816, 41.081818181818186, 35.64545454545455, 30.20909090909091, 24.772727272727273, 19.336363636363636, 13.9]}
{"err": 0.9090909090909091, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [3.3, 11.372727272727271, 19.445454545454545, 27.51818181818182, 35.590909090909086, 43.66363636363636, 51.736363636363635, 59.809090909090905, 67.88181818181818, 75.95454545454545, 84.02727272727272, 92.1], "js": [3.299999999999997, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1, 92.1], "py": [3.3, 11.372727272727271, 19.445454545454545, 27.51818181818182, 35.590909090909086, 43.66363636363636, 51.736363636363635, 59.809090909090905, 67.88181818181818, 75.95454545454545, 84.02727272727272, 92.1]}
{"err": 0.909090909090909, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [54.8, 51.17272727272727, 46.54545454545455, 41.918181818181814, 39.29090909090909, 35.663636363636364, 32.03636363636363, 28.409090909090907, 23.78181818181818, 22.154545454545456, 17.52727272727273, 14.9], "js": [54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 54.8, 14.9], "py": [54.8, 51.17272727272727, 47.54545454545455, 43.918181818181814, 40.29090909090909, 36.663636363636364, 33.03636363636363, 29.409090909090907, 25.78181818181818, 22.154545454545456, 18.52727272727273, 14.9]}
{"err": 0.909090909090909, "x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], "y": [5.9, 8.372727272727273, 8.845454545454547, 11.31818181818182, 14.790909090909093, 17.263636363636365, 20.73636363636364, 22.20909090909091, 23.681818181818187, 27.154545454545456, 28.627272727272732, 33.1], "js": [5.899999999999999, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1, 33.1], "py": [5.9, 8.372727272727273, 10.845454545454547, 13.31818181818182, 15.790909090909093, 18.263636363636365, 20.73636363636364, 23.20909090909091, 25.681818181818187, 28.154545454545456, 30.627272727272732, 33.1]}

exec
/bin/zsh -lc "sed -n '1,135p' tests/js/local_lm_descent.test.js; rg --files tests/js | rg 'batch|stack|local_lm|bg_window|endpoint|stale'; sed -n '9800,9830p' templates/index.html; sed -n '4680,4705p' templates/index.html; sed -n '8125,8155p' templates/index.html; sed -n '10585,10605p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState'];
const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub, bg);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub, bg);
    assert.ok(chi1 < 0.5 * chi0, `${target}: residual must drop substantially (before ${chi0.toExponential(3)}, after ${chi1.toExponential(3)})`);
    const moved = env.state.peaks.some((p, i) => Math.abs(p.center - initial[i].center) > 1e-3 || Math.abs(p.fwhm / initial[i].fwhm - 1) > 1e-3);
    assert.ok(moved, `${target}: at least one free centre/width must move — the shipped code returned the starting model on 18/18 targets`);
    assert.ok(env.state.fitResult && env.state.fitResult.status === 'converged', 'a converged local fit records status: converged');
  }
});

test('A01 replay: the linked U 4f pair also descends', () => {
  const tabs = loadProjectTabs();
  const env = makeEnv();
  const { be, bgSub, bg } = batchTarget(env, tabs, 'U4f Scan', 'U4f Scan_3');
  const chi0 = residualSS(env, be, bgSub, bg);
  const out = env.runFitLocal(be, bgSub, bg);
  assert.equal(out.success, true);
  assert.ok(residualSS(env, be, bgSub, bg) < 0.5 * chi0);
  const parent = env.state.peaks.find(p => !p.linked && p.shape === 'LACX');
  const child = env.state.peaks.find(p => p.linked);
  assert.ok(Math.abs(child.center - (parent.center + child.linkOffset)) < 1e-9, 'linked centre follows the parent');
  assert.ok(Math.abs(child.amplitude - parent.amplitude * child.linkRatio) < 1e-6, 'linked amplitude follows the parent');
});

test('noiseless Gaussian: amplitude 10 started at 5 is recovered', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const truth = { id: 1, name: 'g', shape: 'Gaussian', center: 285.0, fwhm: 1.2, amplitude: 10, glMix: 50, asymmetry: 0 };
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
tests/js/batch_propagation.test.js
tests/js/local_lm_descent.test.js
tests/js/bg_window_indices.test.js
tests/js/local_lm_server_parity_backend.py
tests/js/find_peaks_endpoint_avg.test.js
tests/js/stale_statistics.test.js
tests/js/endpoint_avg_default.test.js
  if (_ob) _ob.remove();

  if (!corrBE.length) {
    renderEmptyChart();
    return;
  }

  // After a fit, freeze all curve data to the stored fit state so that
  // changing ROI never re-draws or recomputes the fit, background, or peaks.
  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
                     state.fitResult.be.length > 0 &&
                     Array.isArray(state.fitResult.bgIntensity) &&
                     state.fitResult.bgIntensity.length === state.fitResult.be.length);

  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
  const plotBG = haveFit ? state.fitResult.bgIntensity
                         : (be.length ? computeBackground(be, inten) : []);
  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
                    : inten;
  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                       ? state.fitResult.bgSubtracted
                       : plotInten.map((v, i) => v - plotBG[i]);

  const modelFull = evalAllPeaks(plotBE, state.peaks);
  // Use backend fitted_y when available (authoritative lmfit result);
  // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
  // F1: never a stale result's curve (Find Peaks apply / undo keep the old
}

// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
function _invalidateFittedY() {
  if (state.fitResult) state.fitResult.fittedY = null;
}

function _clampShirleyIter() {
  const el = document.getElementById('shirley-iter');
  let v = parseInt(el.value);
  if (isNaN(v)) return;
  if (v < 1) el.value = 1;
  else if (v > 50) el.value = 50;
}

// The background window. The user types two binding energies; the window
// is every grid point with lo <= BE <= hi, INCLUSIVE at both ends — the same
// rule getROIData uses for the ROI. This is the single definition shared by
// the preview (computeBackgroundCore) and both /api/fit request builders,
// which send end_idx = i1 + 1 because the backend slices Python-end-exclusive
// (unit 1c of docs/superpowers/plans/2026-09-02-background-architecture-
// sealed-fit-record.md, round-5 amendment — before 1c the builders sent the
// nearest grid index per bound and end_idx = i1, so the fit anchored one
// point inside the window the user drew).
// Returns inclusive indices { i0, i1 }. A blank/NaN bound, or fewer than two
// grid points inside the bounds, falls back to the full range.
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
  try {
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
        const dx = Math.abs(be[i] - be[i - 1]);
        return sum + 0.5 * (yArr[i - 1] + y) * dx;
      }, 0)
    };
  });

  const stats = state.fitResult ? {
    chi: state.fitResult.chi,
    chiReduced: state.fitResult.chiReduced,
    rmse: state.fitResult.rmse,
    rFactor: state.fitResult.rFactor || null,   // F1: the fit's own R (restored only while current)
    // Engine identity travels with the statistic so a reloaded local-engine
    // result is never relabelled as chi-square (unit A0).
    engine: state.fitResult.engine || null,
    objective: state.fitResult.objective || null,
    weighting: state.fitResult.weighting || null,
    status: state.fitResult.status || null,
    starts: _startsForSave(_startsIfCurrent(state.fitResult, _startsLiveKey())),
    startsModelKey: state.fitResult.startsModelKey || null,
    chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
    // Derived from the objective so an older local result (saved before

 succeeded in 26734ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: the cases include the committed real U 4f scan, ascending and descending
ok 1 - the cases include the committed real U 4f scan, ascending and descending
  ---
  duration_ms: 1.240869
  type: 'test'
  ...
# Subtest: shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 2 - shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1909.418236
  type: 'test'
  ...
# Subtest: shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 3 - shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1742.527373
  type: 'test'
  ...
# Subtest: smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 4 - smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1940.189329
  type: 'test'
  ...
# Subtest: smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 5 - smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1808.916951
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 6 - smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1825.379654
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 7 - smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1916.926538
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 8 - tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1745.835227
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 9 - tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1675.170593
  type: 'test'
  ...
# Subtest: linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 10 - linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1678.037367
  type: 'test'
  ...
# Subtest: linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 11 - linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1740.163485
  type: 'test'
  ...
# Subtest: below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)
ok 12 - below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)
  ---
  duration_ms: 3467.37108
  type: 'test'
  ...
# Subtest: KNOWN GAP (Task 4 cause 4, not this unit): linear interpolates by index on the page, by energy on the server — equal on uniform grids only
ok 13 - KNOWN GAP (Task 4 cause 4, not this unit): linear interpolates by index on the page, by energy on the server — equal on uniform grids only
  ---
  duration_ms: 1656.315857
  type: 'test'
  ...
# Subtest: KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
ok 14 - KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
  ---
  duration_ms: 1886.631291
  type: 'test'
  ...
1..14
# tests 14
# suites 0
# pass 14
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 25006.725813

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting,numpy as np,subprocess,json
cases=[]
for n in [3,4,5]:
 for a in [0.1,0.2,0.3,1.1,2.2,4.3,6.1,10.1,20.2,22.7,100.1]:
  for b in [0.1,0.2,0.3,1.1,2.2,4.3,6.1,10.1,20.2,22.7,100.1]:
   if a==b: continue
   y=np.round(np.linspace(a,b,n),1);y[1:-1]-=0.1
   for desc in [False,True]:
    x=np.arange(n,dtype=float)
    if desc:x=x[::-1]
    cases.append(dict(x=x.tolist(),y=y.tolist()))
code=\"\"\"const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');function get(h){return new Function(h.slice(h.indexOf('\\''function shirleyBackground('\\''),h.indexOf('\\''function smartBackground('\\''))+'\\'';return shirleyBackground'\\'')();}const fn=get(fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'')),old=get(cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''cbf3058:templates/index.html'\\''],{encoding:'\\''utf8'\\''}));const cases=JSON.parse(fs.readFileSync(0,'\\''utf8'\\''));console.log(JSON.stringify(cases.map(c=>({js:fn(c.x,c.y,200),old:old(c.x,c.y,200)}))));\"\"\"
out=json.loads(subprocess.check_output(['\\''node'\\'','\\''-e'\\'',code],input=json.dumps(cases),text=True))
found=[]
for c,r in zip(cases,out):
 p=fitting.shirley_background(np.array(c['\\''x'\\'']),np.array(c['\\''y'\\'']))
 e=np.max(np.abs(p-r['\\''js'\\'']))/np.ptp(c['\\''y'\\''])
 se=np.max(np.abs(np.minimum(p,c['\\''y'\\''])-np.minimum(r['\\''js'\\''],c['\\''y'\\''])))/np.ptp(c['\\''y'\\''])
 if e>0.01:found.append(dict(**c,**r,py=p.tolist(),err=e,smartErr=se))
print('\\''FAILS'\\'',len(found))
for r in sorted(found,key=lambda r:(len(r['\\''x'\\'']),-r['\\''smartErr'\\'']))[:14]: print(json.dumps(r))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1680ms:
/Users/skyefortier/.matplotlib is not a writable directory
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Zf1nUS8N' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NmEmnTyi' (errno=Operation not permitted)
FAILS 126
{"x": [0.0, 1.0, 2.0], "y": [1.1, 0.5, 0.2], "js": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.65, 0.2], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [1.1, 0.5, 0.2], "js": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.6500000000000001, 0.2], "err": 0.4999999999999999, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [4.3, 2.1, 0.1], "js": [4.3, 4.3, 0.1], "old": [4.3, 2.2, 0.1], "py": [4.3, 2.1999999999999997, 0.1], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [4.3, 2.1, 0.1], "js": [4.3, 4.3, 0.1], "old": [4.3, 2.2, 0.1], "py": [4.3, 2.2, 0.1], "err": 0.4999999999999999, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [4.3, 2.1999999999999997, 0.3], "js": [4.3, 4.3, 0.3], "old": [4.3, 2.3, 0.3], "py": [4.3, 2.3, 0.3], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [4.3, 2.1999999999999997, 0.3], "js": [4.3, 4.3, 0.3], "old": [4.3, 2.3, 0.3], "py": [4.3, 2.3, 0.3], "err": 0.5, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [6.1, 3.0, 0.1], "js": [6.1, 6.1, 0.1], "old": [6.1, 3.1, 0.1], "py": [6.1, 3.0999999999999996, 0.1], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [6.1, 3.0, 0.1], "js": [6.1, 6.1, 0.1], "old": [6.1, 3.1, 0.1], "py": [6.1, 3.1, 0.1], "err": 0.49999999999999994, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [6.1, 3.1, 0.3], "js": [6.1, 6.1, 0.3], "old": [6.1, 3.1999999999999997, 0.3], "py": [6.1, 3.1999999999999997, 0.3], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [6.1, 3.1, 0.3], "js": [6.1, 6.1, 0.3], "old": [6.1, 3.1999999999999997, 0.3], "py": [6.1, 3.1999999999999997, 0.3], "err": 0.5, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [6.1, 3.5, 1.1], "js": [6.1, 6.1, 1.1], "old": [6.1, 3.6, 1.1], "py": [6.1, 3.5999999999999996, 1.1], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [6.1, 3.5, 1.1], "js": [6.1, 6.1, 1.1], "old": [6.1, 3.6, 1.1], "py": [6.1, 3.6, 1.1], "err": 0.4999999999999999, "smartErr": 0.0}
{"x": [0.0, 1.0, 2.0], "y": [10.1, 5.0, 0.1], "js": [10.1, 10.1, 0.1], "old": [10.1, 5.1, 0.1], "py": [10.1, 5.1, 0.1], "err": 0.5, "smartErr": 0.0}
{"x": [2.0, 1.0, 0.0], "y": [10.1, 5.0, 0.1], "js": [10.1, 10.1, 0.1], "old": [10.1, 5.1, 0.1], "py": [10.1, 5.1, 0.1], "err": 0.5, "smartErr": 0.0}

codex
All 14 committed parity tests pass with the read-only import workaround. I found another substantial mismatch on finite, below-baseline data: rounding in the initial line can turn numerical residue into an integral that changes the whole curve. I’m reducing it to a small reproducible case and checking whether it persists at 200 iterations.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''),fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args?.[0]?.endsWith('\\''_backend.py'\\''))return orig(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return orig(file,args,opts);};
const file=path.resolve('\\''tests/js/background_parity.test.js'\\''),source=fs.readFileSync(file,'\\''utf8'\\'');
for(const ref of ['\\''cbf3058'\\'','\\''895f323'\\'']){
 const html=orig('\\''git'\\'',['\\''show'\\'',ref+'\\'':templates/index.html'\\''],{encoding:'\\''utf8'\\''});
 const results=[];
 const req=name=>name==='\\''node:test'\\''?{test:(label,fn)=>{try{fn();results.push({label,pass:true})}catch(e){results.push({label,pass:false,error:e.message})}}}:name==='\\''node:fs'\\''?{...fs,readFileSync:(p,...args)=>String(p).endsWith('\\''templates/index.html'\\'')?html:fs.readFileSync(p,...args)}:require(name);
 new Function('\\''require'\\'','\\''__dirname'\\'',source)(req,path.dirname(file));
 console.log(JSON.stringify({ref,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>"'!r.pass)}));
}'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''child_process'\\'');const orig=cp.execFileSync;cp.execFileSync=function(file,args,opts){if(args?.[0]?.endsWith('\\''_backend.py'\\''))return orig(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return orig(file,args,opts);};for(const file of ['\\''local_lm_descent'\\'','\\''batch_propagation'\\'','\\''bg_window_indices'\\'','\\''endpoint_avg_default'\\'','\\''find_peaks_endpoint_avg'\\'','\\''tougaard_twin'\\''])require('\\''./tests/js/'\\''+file+'\\''.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 9083ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 1 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1369.438702
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 2 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 234.293885
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 3 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 14.232406
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 4 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.970169
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 5 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 14.552574
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 6 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 10.581244
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 7 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 10.7418
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 8 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 11.586365
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 9 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 48.892246
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 10 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 28.782729
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 11 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.156985
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 12 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 14.331788
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 13 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 13.010133
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 14 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.264739
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 15 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.290743
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 16 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1417.497284
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 17 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 66.505084
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 18 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 24.654355
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 19 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 14.940779
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 20 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 93.05175
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 21 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1403.78079
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 22 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 23.521065
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 23 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 11.927931
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 24 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 9.79424
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
ok 25 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 4034.435891
  type: 'test'
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 26 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 21.135857
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 27 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 24.02666
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 28 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 23.675632
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 29 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 10.460817
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 30 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 10.669365
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 31 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 11.613328
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 32 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 30.780854
  type: 'test'
  ...
# Subtest: source ROI overwrites a different target ROI during propagation
ok 33 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 0.21446
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 34 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.102478
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 35 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.184634
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 36 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.134062
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 37 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.112015
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 38 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 0.815578
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 39 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 0.120287
  type: 'test'
  ...
# Subtest: window at the ROI bounds covers every point, including the last one
ok 40 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 0.207155
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 41 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.140162
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 42 - bound order does not matter
  ---
  duration_ms: 0.153389
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 43 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.163167
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 44 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.208741
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 45 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.156422
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 46 - exactly two points in range is a usable window
  ---
  duration_ms: 0.143978
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 47 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 0.83446
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 48 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 0.617358
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 49 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 1.024572
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 50 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 0.674325
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 51 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 0.736879
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 52 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 0.689422
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 53 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 0.742967
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 54 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.47746
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 55 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.351455
  type: 'test'
  ...
# Subtest: runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
ok 56 - runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
  ---
  duration_ms: 0.507289
  type: 'test'
  ...
# Subtest: _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
ok 57 - _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
  ---
  duration_ms: 0.364545
  type: 'test'
  ...
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 58 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 10.813206
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 59 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.719432
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 60 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.364635
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 61 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 2.973002
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 62 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 2.069922
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 63 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 1.095219
  type: 'test'
  ...
1..63
# tests 63
# suites 0
# pass 63
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 9124.585526

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting,numpy as np,subprocess,json
cases=[]
for x,y in [([0,1,2],[1.1,.5,.2]),([2,1,0],[.2,.5,1.1]),([2,1,0],[1.1,.5,.2]),([0,1],[1.1,.2]),([0,0,1,2],[10,30,25,20]),([0,0,0],[10,30,20]),([0,1,3,6],[10,30,25,20]),([6,3,1,0],[20,25,30,10])]:
 for it in [0,1,5,50,200]:
  cases.append(dict(x=x,y=y,it=it))
code=\"\"\"const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');function get(h){const lines=h.split('\\''\\\\n'\\'');function fn(name){let st=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')),d=0;for(let i=st;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(st,i+1).join('\\''\\\\n'\\'');}}return new Function(['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''].map(fn).join('\\''\\\\n'\\'')+'\\'';return {shirleyBackground,computeBackgroundCore}'\\'')();}const js=get(fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''));const old=get(cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''cbf3058:templates/index.html'\\''],{encoding:'\\''utf8'\\''}));const cases=JSON.parse(fs.readFileSync(0,'\\''utf8'\\''));console.log(JSON.stringify(cases.map(c=>({js:js.shirleyBackground(c.x,c.y,c.it),core:js.computeBackgroundCore(c.x,c.y,{bgType:'\\''shirley'\\'',shirleyIter:String(c.it),endpointAvg:'\\''1'\\'',bgStart:'\\'''\\'',bgEnd:'\\'''\\''}),old:old.shirleyBackground(c.x,c.y,c.it)}))));\"\"\"
out=json.loads(subprocess.check_output(['\\''node'\\'','\\''-e'\\'',code],input=json.dumps(cases),text=True))
for c,r in zip(cases,out):
 p=fitting.shirley_background(np.array(c['\\''x'\\''],float),np.array(c['\\''y'\\''],float),n_iter=c['\\''it'\\''])
 if c['\\''y'\\'']==[1.1,.5,.2] or c['\\''y'\\'']==[.2,.5,1.1]: print(json.dumps(dict(**c,**r,py=p.tolist())))
 elif not np.allclose(r['\\''js'\\''],p,rtol=0,atol=1e-6): print('\\''EDGE_FAIL'\\'',c,r,p.tolist())
print('\\''OTHER EDGE CASES COMPLETE'\\'')
x=np.array([0.,1.,2.])
for y in [[1,float('\\''nan'\\''),2],[1,float('\\''inf'\\''),2],[1,float('\\''-inf'\\''),2]]:
 with np.errstate(all='\\''ignore'\\''): print('\\''NONFINITE PY'\\'',y,fitting.shirley_background(x,np.array(y)).tolist())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4417,4443p'; nl -ba tests/js/background_parity.test.js | sed -n '83,104p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
  4417	  // is fitting.py's ascending-copy form mirrored.
  4418	  const n = be.length;
  4419	  if (n < 2) return new Array(n).fill(0);
  4420	  const I0 = intensity[0], I1 = intensity[n - 1];
  4421	  let bg = intensity.map((_, i) => I0 + (I1 - I0) * i / (n - 1));
  4422	  for (let iter = 0; iter < maxIter; iter++) {
  4423	    const cum = new Array(n).fill(0);            // cum[i] = ∫ net signal from point i to the array end
  4424	    let sPrev = Math.max(intensity[n - 1] - bg[n - 1], 0);
  4425	    for (let j = n - 2; j >= 0; j--) {
  4426	      const sj = Math.max(intensity[j] - bg[j], 0);
  4427	      cum[j] = cum[j + 1] + 0.5 * (sj + sPrev) * Math.abs(be[j + 1] - be[j]);
  4428	      sPrev = sj;
  4429	    }
  4430	    const total = cum[0];
  4431	    if (!(total > 0)) break;                     // no net signal left: keep the current background
  4432	    let maxChange = 0;
  4433	    const next = new Array(n);
  4434	    for (let i = 0; i < n; i++) {
  4435	      next[i] = I1 + (I0 - I1) * cum[i] / total;
  4436	      const d = Math.abs(next[i] - bg[i]);
  4437	      if (d > maxChange) maxChange = d;
  4438	    }
  4439	    bg = next;
  4440	    if (maxChange < 1e-6) break;                 // fitting.py's tolerance
  4441	  }
  4442	  return bg;
  4443	}
    83	// Codex round 1: data that dip below the baseline. With the clamp but the old
    84	// zero start and index-linear fallback, the JS reached another fixed point
    85	// (33–58 % of the span); fitting.py starts from the straight line and keeps it
    86	// when no net signal is left. Exact small cases, every iteration count.
    87	const BELOW = [
    88	  { be: [0, 1, 2, 3, 4], inten: [10, 5, 5, 17, 20] },
    89	  { be: [3.5, 1.1, 1, 0], inten: [6, 7, 13, 19] },
    90	  { be: [3, 2, 1, 0], inten: [100, 107, 120, 127] },
    91	  { be: [0, 1, 3, 6, 10], inten: [10, 5, 5, 17, 20] },
    92	];
    93	test('below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)', () => {
    94	  for (const method of ['shirley', 'smart']) {
    95	    const server = py({ mode: 'bg', items: BELOW.map(c => ({ method, be: c.be, inten: c.inten, n_avg: 1 })) });
    96	    BELOW.forEach((c, k) => {
    97	      for (const it of [5, 50, 200]) {
    98	        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '1', bgStart: '', bgEnd: '' });
    99	        const rel = maxRelDiff(js, server[k], span(c.inten));
   100	        assert.ok(rel <= TOL, `${method} ${JSON.stringify(c.be)} at ${it} iterations: ${rel.toExponential(2)} of the span (js ${js.map(v => v.toFixed(3))}, server ${server[k].map(v => v.toFixed(3))})`);
   101	      }
   102	    });
   103	  }
   104	});
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gExw9hj3' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3jg2vL5M' (errno=Operation not permitted)
?? docs/autofit/codex/background_twins_r2_verdict_runA.md
?? docs/autofit/codex/background_twins_r2_verdict_runB.md

 succeeded in 1791ms:
/Users/skyefortier/.matplotlib is not a writable directory
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sg4hrlcz' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-F0KWiIT9' (errno=Operation not permitted)
{"x": [0, 1, 2], "y": [1.1, 0.5, 0.2], "it": 0, "js": [1.1, 0.65, 0.19999999999999996], "core": [1.1, 1.1, 0.2], "old": [0, 0, 0], "py": [1.1, 0.65, 0.2]}
{"x": [0, 1, 2], "y": [1.1, 0.5, 0.2], "it": 1, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.47391304347826096, 0.2], "py": [1.1, 0.65, 0.2]}
{"x": [0, 1, 2], "y": [1.1, 0.5, 0.2], "it": 5, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.65, 0.2]}
{"x": [0, 1, 2], "y": [1.1, 0.5, 0.2], "it": 50, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.65, 0.2]}
{"x": [0, 1, 2], "y": [1.1, 0.5, 0.2], "it": 200, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.65, 0.2]}
{"x": [2, 1, 0], "y": [0.2, 0.5, 1.1], "it": 0, "js": [0.2, 0.6500000000000001, 1.1], "core": [0.2, 0.6500000000000001, 1.1], "old": [0, 0, 0], "py": [0.2, 0.65, 1.1]}
{"x": [2, 1, 0], "y": [0.2, 0.5, 1.1], "it": 1, "js": [0.2, 0.6500000000000001, 1.1], "core": [0.2, 0.6500000000000001, 1.1], "old": [0.19999999999999996, 0.4739130434782608, 1.1], "py": [0.2, 0.65, 1.1]}
{"x": [2, 1, 0], "y": [0.2, 0.5, 1.1], "it": 5, "js": [0.2, 0.6500000000000001, 1.1], "core": [0.2, 0.6500000000000001, 1.1], "old": [0.19999999999999996, 1.1, 1.1], "py": [0.2, 0.65, 1.1]}
{"x": [2, 1, 0], "y": [0.2, 0.5, 1.1], "it": 50, "js": [0.2, 0.6500000000000001, 1.1], "core": [0.2, 0.6500000000000001, 1.1], "old": [0.19999999999999996, 1.1, 1.1], "py": [0.2, 0.65, 1.1]}
{"x": [2, 1, 0], "y": [0.2, 0.5, 1.1], "it": 200, "js": [0.2, 0.6500000000000001, 1.1], "core": [0.2, 0.6500000000000001, 1.1], "old": [0.19999999999999996, 1.1, 1.1], "py": [0.2, 0.65, 1.1]}
{"x": [2, 1, 0], "y": [1.1, 0.5, 0.2], "it": 0, "js": [1.1, 0.65, 0.19999999999999996], "core": [1.1, 1.1, 0.2], "old": [0, 0, 0], "py": [1.1, 0.6500000000000001, 0.2]}
{"x": [2, 1, 0], "y": [1.1, 0.5, 0.2], "it": 1, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.47391304347826096, 0.2], "py": [1.1, 0.6500000000000001, 0.2]}
{"x": [2, 1, 0], "y": [1.1, 0.5, 0.2], "it": 5, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.6500000000000001, 0.2]}
{"x": [2, 1, 0], "y": [1.1, 0.5, 0.2], "it": 50, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.6500000000000001, 0.2]}
{"x": [2, 1, 0], "y": [1.1, 0.5, 0.2], "it": 200, "js": [1.1, 1.1, 0.2], "core": [1.1, 1.1, 0.2], "old": [1.1, 0.6500000000000001, 0.2], "py": [1.1, 0.6500000000000001, 0.2]}
OTHER EDGE CASES COMPLETE
NONFINITE PY [1, nan, 2] [nan, nan, nan]
NONFINITE PY [1, inf, 2] [nan, nan, nan]
NONFINITE PY [1, -inf, 2] [1.0, 1.5, 2.0]

 succeeded in 51768ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
{"ref":"cbf3058","pass":13,"fail":[{"label":"below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)","pass":false,"error":"shirley [0,1,2,3,4] at 5 iterations: 3.33e-1 of the span (js 10.000,10.000,10.000,15.000,20.000, server 10.000,12.500,15.000,17.500,20.000)"}]}
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-al7E4pxr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-k3QtNPem' (errno=Operation not permitted)
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
{"ref":"895f323","pass":9,"fail":[{"label":"shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case","pass":false,"error":"synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span"},{"label":"shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case","pass":false,"error":"synthetic C 1s, 101 pts, ascending: 2.07e-4 of the span"},{"label":"smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case","pass":false,"error":"synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span"},{"label":"smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case","pass":false,"error":"synthetic C 1s, 101 pts, ascending: 7.17e-3 of the span"},{"label":"below-baseline data: shirley and smart equal fitting.py at 5, 50 and 200 iterations (Codex round 1)","pass":false,"error":"shirley [3,2,1,0] at 5 iterations: 9.26e-2 of the span (js 100.000,109.000,118.000,127.000, server 100.000,107.000,120.500,127.000)"}]}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import importlib.util,json,subprocess,numpy as np
spec=importlib.util.spec_from_file_location('\\''bridge'\\'','\\''tests/js/background_parity_backend.py'\\'');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=m.cases();req=[]
for method in ['\\''shirley'\\'','\\''smart'\\'']:
 for avg in [1,10]:
  for it in [5,200]:
   for c in cases:req.append(dict(**c,method=method,avg=avg,it=it))
code=\"\"\"const fs=require('\\''fs'\\'');const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),ls=h.split('\\''\\\\n'\\'');function f(name){let s=ls.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')),d=0;for(let i=s;i<ls.length;i++){for(const c of ls[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return ls.slice(s,i+1).join('\\''\\\\n'\\'');}}const j=new Function(['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''].map(f).join('\\''\\\\n'\\'')+'\\'';return computeBackgroundCore'\\'')();console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'\\''utf8'\\'')).map(c=>j(c.be,c.inten,{bgType:c.method,shirleyIter:String(c.it),endpointAvg:String(c.avg),bgStart:'\\'''\\'',bgEnd:'\\'''\\''}))));\"\"\"
out=json.loads(subprocess.check_output(['\\''node'\\'','\\''-e'\\'',code],input=json.dumps(req),text=True))
summary={}
for c,js in zip(req,out):
 py=m.FUNCS[c['\\''method'\\'']](np.array(c['\\''be'\\'']),np.array(c['\\''inten'\\'']),c['\\''avg'\\''])
 key=f\"{c['\\''method'\\'']} avg={c['\\''avg'\\'']} iter={c['\\''it'\\'']}\"
 summary[key]=max(summary.get(key,0),float(np.max(np.abs(py-js))/np.ptp(c['\\''inten'\\''])*100))
print(json.dumps(summary))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1660ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"shirley avg=1 iter=5": 0.0034523133317384933, "shirley avg=1 iter=200": 2.343798201997976e-14, "shirley avg=10 iter=5": 0.005023043595289742, "shirley avg=10 iter=200": 9.375192807991904e-14, "smart avg=1 iter=5": 0.0034523133317384933, "smart avg=1 iter=200": 2.343798201997976e-14, "smart avg=10 iter=5": 0.005023043595289742, "smart avg=10 iter=200": 9.375192807991904e-14}

codex
The reduced case is `be=[0,1,2]`, intensity `[1.1,0.5,0.2]`. Python keeps `[1.1,0.65,0.2]`; the new JS returns `[1.1,1.1,0.2]` at 1, 5, 50 and 200 iterations—a 50% span error. The cause is the initial endpoint rounding below `0.2`, whereas NumPy pins it exactly. The new regression test does fail on `cbf3058`, and all 63 selected adjacent tests pass.
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');const f=new Function(h.slice(h.indexOf('\\''function shirleyBackground('\\''),h.indexOf('\\''function smartBackground('\\''))+'\\'';return shirleyBackground'\\'')();for(const y of [[1,NaN,2],[1,Infinity,2],[1,-Infinity,2]])console.log(y.map(String),f([0,1,2],y,200).map(String));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
[ '1', 'NaN', '2' ] [ '1', '1.5', '2' ]
[ '1', 'Infinity', '2' ] [ 'NaN', 'NaN', '2' ]
[ '1', '-Infinity', '2' ] [ '1', '1.5', '2' ]

codex
1. **MAJOR — Initial-line rounding creates a different fixed point.** [templates/index.html:4421](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4421)

   Reproducer: `be=[0,1,2]`, `intensity=[1.1,0.5,0.2]`, endpoint averaging `1`.

   | Implementation | Shirley background |
   |---|---|
   | Python | `[1.1,0.65,0.2]` |
   | Round-2 JS | `[1.1,1.1,0.2]` |

   Confirmed through `computeBackgroundCore` at **1, 5, 50 and 200 iterations**: **50% of the intensity span**. At 200 iterations, `cbf3058` agrees with Python on this case.

   JS initializes the last background value to `0.19999999999999996`; NumPy’s `linspace` pins it exactly to `0.2`. The resulting tiny positive endpoint signal becomes the entire integral, moving the middle background to `1.1`. The next iteration finds zero signal and preserves that incorrect curve. Reversing both arrays also changes the JS result, contradicting order invariance.

   This reaches display, frozen backgrounds, local/Batch Fit inputs and stack reconstruction. Match Python’s initialization—including exact endpoints and arithmetic order—and add decimal-valued regression cases in both directions. The new integer-intensity cases miss this failure.

Validation: **14 parity tests and 63 adjacent tests pass**. The new below-baseline test fails against `cbf3058`; the four original parity failures reproduce against `895f323`. Documented measurements reproduce, and both known-gap pins pass. Python-backed checks required an in-memory workaround for the sandbox’s temporary-directory probe. No files changed.

**VERDICT: NO-GO**
tokens used
78,177
1. **MAJOR — Initial-line rounding creates a different fixed point.** [templates/index.html:4421](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4421)

   Reproducer: `be=[0,1,2]`, `intensity=[1.1,0.5,0.2]`, endpoint averaging `1`.

   | Implementation | Shirley background |
   |---|---|
   | Python | `[1.1,0.65,0.2]` |
   | Round-2 JS | `[1.1,1.1,0.2]` |

   Confirmed through `computeBackgroundCore` at **1, 5, 50 and 200 iterations**: **50% of the intensity span**. At 200 iterations, `cbf3058` agrees with Python on this case.

   JS initializes the last background value to `0.19999999999999996`; NumPy’s `linspace` pins it exactly to `0.2`. The resulting tiny positive endpoint signal becomes the entire integral, moving the middle background to `1.1`. The next iteration finds zero signal and preserves that incorrect curve. Reversing both arrays also changes the JS result, contradicting order invariance.

   This reaches display, frozen backgrounds, local/Batch Fit inputs and stack reconstruction. Match Python’s initialization—including exact endpoints and arithmetic order—and add decimal-valued regression cases in both directions. The new integer-intensity cases miss this failure.

Validation: **14 parity tests and 63 adjacent tests pass**. The new below-baseline test fails against `cbf3058`; the four original parity failures reproduce against `895f323`. Documented measurements reproduce, and both known-gap pins pass. Python-backed checks required an in-memory workaround for the sandbox’s temporary-directory probe. No files changed.

**VERDICT: NO-GO**
