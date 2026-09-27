OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e227-7a2c-7c10-a27b-d604a56b5047
--------
user
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

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll review the diff and callers, check the parity bridge against `run_fit`, and probe the edge cases you listed. I’ll keep it read-only and finish with ranked findings and a verdict.
exec
/bin/zsh -lc "pwd && git status --short && git diff --stat 895f323..HEAD && rg --files -g 'AGENTS.md' -g 'CLAUDE.md'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-u4P6GMT5' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3Mnz84hO' (errno=Operation not permitted)
?? docs/autofit/codex/background_twins_verdict_runA.md
?? docs/autofit/codex/background_twins_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kFPth3eg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Y75TkFkp' (errno=Operation not permitted)
 CLAUDE.md                                          | 12 +++
 .../codex/background_twins_review_prompt.txt       | 53 +++++++++++++
 .../plans/2026-09-27-background-twins.md           | 55 +++++++++++++
 templates/index.html                               | 22 ++++--
 tests/js/background_parity.test.js                 | 90 ++++++++++++++++++++++
 tests/js/background_parity_backend.py              | 84 ++++++++++++++++++++
 6 files changed, 311 insertions(+), 5 deletions(-)
CLAUDE.md

exec
/bin/zsh -lc "cat docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md; rg -n 'def (shirley_background|smart_background|smart_exp_background|tougaard_background|run_fit)|shirleyBackground\\(|smartBackground\\(|computeBackgroundCore\\(' fitting.py templates/index.html; cat package.json" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 0ms:
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
fitting.py:338:def shirley_background(
fitting.py:402:def smart_background(
fitting.py:546:def tougaard_background(
fitting.py:2094:def run_fit(*args, cancel=None, **kwargs):
templates/index.html:4408:function shirleyBackground(be, intensity, maxIter) {
templates/index.html:4438:function smartBackground(be, intensity, maxIter, rawIntensity) {
templates/index.html:4449:  const shir = shirleyBackground(be, intensity, maxIter);
templates/index.html:4728:function computeBackgroundCore(be, intensity, settings) {
templates/index.html:4748:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
templates/index.html:4749:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
templates/index.html:4779:  return computeBackgroundCore(be, intensity, {
templates/index.html:9261:  return computeBackgroundCore(be, inten, settings);
cat: package.json: No such file or directory

exec
/bin/zsh -lc 'git diff 895f323..HEAD -- templates/index.html tests/js/background_parity.test.js tests/js/background_parity_backend.py CLAUDE.md docs/superpowers/plans/2026-09-27-background-twins.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tZ9hREcn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LcJu2MA4' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 7f03bea..6cd3464 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -743,6 +743,18 @@ starting model as "Fit complete"; see
 | `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
 | `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |
 
+The page's background twins (`computeBackgroundCore`: what it draws, freezes
+into `fitResult.bgIntensity` at fit time, saves, and what the local engine
+fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
+iteration count for shirley, smart, smart_exp, tougaard and linear, with
+endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
+2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
+against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
+the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
+descending grids; the UI's Shirley iteration count (default 5) leaves
+0.016–0.019 % of the span of unfinished iteration (Part 5 of the
+sealed-fit-record memo).
+
 Use Shirley for standard core-level regions. Linear only when the
 spectral window is very narrow and featureless.
 
diff --git a/docs/superpowers/plans/2026-09-27-background-twins.md b/docs/superpowers/plans/2026-09-27-background-twins.md
new file mode 100644
index 0000000..14ed507
--- /dev/null
+++ b/docs/superpowers/plans/2026-09-27-background-twins.md
@@ -0,0 +1,55 @@
+# Unit 4 — the background twins: two JS fixes and a pinned parity test (2026-09-27)
+
+Branch `fix-background-twins`, stacked on `fix-noise-floor-scale-free` (F3):
+deploy F2 → unit 2 → F3 → unit 4. It touches only `shirleyBackground`,
+`smartBackground` and one line of `computeBackgroundCore`; it can be rebased
+onto main alone.
+
+Owner's brief (2026-09-27): "the background parity test plus the two JS
+fixes (JS shirleyBackground missing the net-signal-at-zero clamp; JS smart
+clamping against the averaged array instead of raw). shirley_linear is
+de-listed — pin its divergence as a known gap, don't fix it." Source: Task 4
+(`docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md`), whose
+causes S4 and S5 were proven by exact reconstruction.
+
+## 1. Sites
+
+| # | site | before | after |
+|---|---|---|---|
+| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg`: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | `max(intensity − bg, 0)` in both integrals, as `fitting.shirley_background` (Proctor–Sherwood); the iteration scheme is otherwise untouched (the JS was already order-invariant: descending input gives the same curve as fitting.py's ascending copy) |
+| S5 | `smartBackground(be, intensity, maxIter, rawIntensity)` + `computeBackgroundCore` | clamps `min(shirley, averaged data)` | clamps against the RAW slice (`rawIntensity`, default `intensity`), as `fitting.smart_background`: averaging only ever moves the background, never the reported net counts |
+| — | `shirley_linear` | order-sensitive (27–33 % of the span on descending grids, Task 4 cause 3) | UNCHANGED, de-listed (disabled, hidden); the divergence is pinned as a known gap |
+| — | not changed | the UI's Shirley iteration count (default 5) vs the server's convergence (tolerance 1e-6, ≤ 200) — Part 5 of the sealed-fit-record memo | |
+
+Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
+freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
+what the local engine (Batch Fit, fallback) fits against, and what stack
+Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
+never touch them.
+
+## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)
+
+Max |JS − server| as % of the intensity span:
+
+| method | endpoint avg | iterations | before | after |
+|---|---|---|---|---|
+| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
+| shirley | 10 | 200 | 0.078 % | 0.0000 % |
+| smart | 1 | 200 | 0.047 % | 0.0000 % |
+| smart | 10 | 200 | **1.19 %** | 0.0000 % |
+| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.016–0.019 % (unconverged iteration: Part 5, not this unit) |
+
+## 3. Tests
+
+`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
+(fitting.py's own functions, never a reimplementation): shirley, smart,
+smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
+`computeBackgroundCore` at a converged iteration count, every case within
+1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
+four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
+ascending grids, still diverges on descending ones (pinned; the test fails if
+the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.
+
+## 4. Codex rounds
+
+(filled in as they run)
diff --git a/templates/index.html b/templates/index.html
index 5d38496..655a50c 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4414,13 +4414,18 @@ function shirleyBackground(be, intensity, maxIter) {
   for (let iter = 0; iter < maxIter; iter++) {
     const newBg = new Array(n).fill(0);
     for (let i = 0; i < n; i++) {
+      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
+      // (Proctor–Sherwood): a noise channel below the background contributes
+      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
+      // integrated the raw difference and converged to a different fixed point,
+      // 0.015–0.24 % of the span away from the background the server fits).
       let sumRight = 0;
       for (let j = i; j < n - 1; j++) {
-        sumRight += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
+        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
       }
       let sumTotal = 0;
       for (let j = 0; j < n - 1; j++) {
-        sumTotal += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
+        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
       }
       const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
       newBg[i] = I1 + (I0 - I1) * frac;
@@ -4430,12 +4435,19 @@ function shirleyBackground(be, intensity, maxIter) {
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
 
@@ -4734,7 +4746,7 @@ function computeBackgroundCore(be, intensity, settings) {
   // Compute background on the sliced region — apply endpoint averaging for Shirley types
   let bgSub;
   if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
-  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
+  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
   else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
   else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
   else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
diff --git a/tests/js/background_parity.test.js b/tests/js/background_parity.test.js
new file mode 100644
index 0000000..8c9e728
--- /dev/null
+++ b/tests/js/background_parity.test.js
@@ -0,0 +1,90 @@
+// Unit 4 (2026-09-27): the page's background twins against fitting.py — the
+// curve the page draws, saves and fits locally against must be the one the
+// server fits against. Task 4 (docs/superpowers/plans/2026-09-02-task4-
+// background-twin-parity.md) measured the gaps and proved their causes;
+// this unit fixes the two JS bugs it found and PINS the parity:
+//   S4 shirley: the JS integrated the raw net signal, fitting.py max(y−B, 0)
+//      (0.015–0.24 % of the span at convergence);
+//   S5 smart at endpoint averaging > 1: the JS clamped against the averaged
+//      copy, fitting.py against the raw data (up to 1 % of the span).
+// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
+// descending grids (27–33 % of the span, Task 4 cause 3) is pinned as a KNOWN
+// GAP, not fixed. Convergence semantics (the UI's Shirley iteration count vs
+// the server's tolerance) are Part 5 of the sealed-fit-record memo, not this
+// unit: the JS runs at a converged iteration count here.
+//
+// The JS runs computeBackgroundCore (the page's own dispatcher) extracted
+// verbatim; the Python side calls fitting.py's own functions through
+// tests/js/background_parity_backend.py.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+const { execFileSync } = require('node:child_process');
+
+const REPO_ROOT = path.join(__dirname, '../..');
+const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
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
+const PYTHON = (() => {
+  for (const c of [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
+    if (fs.existsSync(c)) return c;
+  }
+  return 'python3';
+})();
+const BRIDGE = path.join(__dirname, 'background_parity_backend.py');
+const py = req => JSON.parse(execFileSync(PYTHON, [BRIDGE], { input: JSON.stringify(req), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
+
+const JS = new Function([
+  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
+  'linearBackground', 'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
+].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
+  '\nreturn { computeBackgroundCore };')();
+const CONVERGED_ITER = 200;
+const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
+  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });
+
+const CASES = py({ mode: 'cases' });
+const span = y => Math.max(...y) - Math.min(...y);
+function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
+function compare(method, nAvg) {
+  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
+  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
+}
+
+test('the cases include the committed real U 4f scan, ascending and descending', () => {
+  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
+  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
+});
+
+// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
+// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
+// difference between 200 JS iterations and the server's 1e-6-count stopping
+// tolerance.
+const TOL = 1e-6;
+for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
+  for (const nAvg of [1, 10]) {
+    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
+      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
+    });
+  }
+}
+
+test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
+  const rows = compare('shirley_linear', 1);
+  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
+  const desc = rows.filter(r => /descending/.test(r.label));
+  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
+    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
+  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
+});
diff --git a/tests/js/background_parity_backend.py b/tests/js/background_parity_backend.py
new file mode 100644
index 0000000..c321c86
--- /dev/null
+++ b/tests/js/background_parity_backend.py
@@ -0,0 +1,84 @@
+#!/usr/bin/env python3
+"""Backend bridge for tests/js/background_parity.test.js (unit 4, 2026-09-27).
+
+stdin {"mode": "cases"} -> the spectra the parity test runs on: seeded
+synthetic spectra (a narrow C 1s, a wide U 4f doublet) and the committed real
+U 4f Scan_0 (1-GTA UCl4-graphite project), each ascending AND descending.
+stdin {"mode": "bg", "items": [{"method", "be", "inten", "n_avg"}...]} -> the
+background fitting.py's OWN function returns for each (the functions run_fit
+calls for the anchor window, never a reimplementation).
+"""
+import io
+import json
+import os
+import sys
+import zipfile
+
+import numpy as np
+
+ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+sys.path.insert(0, ROOT)
+import fitting  # noqa: E402
+
+FUNCS = {
+    "shirley": lambda x, y, n: fitting.shirley_background(x, y, n_avg=n),
+    "smart": lambda x, y, n: fitting.smart_background(x, y, n_avg=n),
+    "smart_exp": lambda x, y, n: fitting.smart_experimental_background(x, y, n_avg=n),
+    "shirley_linear": lambda x, y, n: fitting.shirley_linear_background(x, y, n_avg=n),
+    "tougaard": lambda x, y, n: fitting.tougaard_background(x, y, n_avg=n),
+    "linear": lambda x, y, n: fitting.linear_background(x, y),
+}
+
+
+def _g(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+def _shirley_step(x, c, a, w, h):
+    # a loss step under each line, high-BE side (makes Shirley non-trivial)
+    return h * a / (1 + np.exp(-(x - c) / (0.4 * w)))
+
+
+def cases():
+    rng = np.random.default_rng(20260927)
+    out = []
+    x = np.linspace(280.0, 295.0, 101)
+    y = rng.poisson(400 + _g(x, 284.5, 6000, 1.0) + _g(x, 286.3, 1200, 1.2) + _shirley_step(x, 284.5, 6000, 1.0, 0.06)).astype(float)
+    out.append(("synthetic C 1s, 101 pts", x, y))
+    x = np.linspace(370.0, 405.0, 351)
+    y = rng.poisson(2000 + _g(x, 380.9, 20000, 1.6) + _g(x, 391.8, 15000, 1.6)
+                    + _shirley_step(x, 380.9, 20000, 1.6, 0.08) + _shirley_step(x, 391.8, 15000, 1.6, 0.08)).astype(float)
+    out.append(("synthetic U 4f doublet, 351 pts", x, y))
+    proj = os.path.join(ROOT, "docs", "autofit", "test_data", "1-GTA UCl4-graphite one set of U doublets.proj.zip")
+    if os.path.exists(proj):
+        with zipfile.ZipFile(proj) as z:
+            man = json.loads(z.read("manifest.json"))
+            for sp in man.get("spectra", []):
+                if sp.get("name") == "U4f Scan_0":
+                    rec = json.loads(z.read(sp["filename"]))
+                    be = np.asarray(rec["rawBE"], float) - float(rec.get("ccShift") or 0)
+                    out.append(("real U 4f Scan_0 (committed project)", be, np.asarray(rec["rawIntensity"], float)))
+                    break
+    res = []
+    for label, x, y in out:
+        asc = np.argsort(x)
+        res.append({"label": label + ", ascending", "be": x[asc].tolist(), "inten": y[asc].tolist()})
+        res.append({"label": label + ", descending", "be": x[asc][::-1].tolist(), "inten": y[asc][::-1].tolist()})
+    return res
+
+
+def main():
+    req = json.load(sys.stdin)
+    if req["mode"] == "cases":
+        json.dump(cases(), sys.stdout)
+        return
+    out = []
+    for it in req["items"]:
+        x = np.asarray(it["be"], float)
+        y = np.asarray(it["inten"], float)
+        out.append([float(v) for v in FUNCS[it["method"]](x, y, int(it["n_avg"]))])
+    json.dump(out, sys.stdout)
+
+
+if __name__ == "__main__":
+    main()

exec
/bin/zsh -lc "sed -n '1,150p' CLAUDE.md; sed -n '300,590p' fitting.py; sed -n '4400,4795p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
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
        if total <= 0.0:
            break
        B = step_h * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    result = np.minimum(linear + B, ys)
    return result[::-1] if flipped else result


def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Single-pass Tougaard universal-cross-section background, with the
    constant (pre-loss) term the window-limited integral cannot generate.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels are read, so neither C0 nor the high-BE anchor rests on a single
    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
    endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.
    """
    n = len(x)
    for (let i = 0; i < N; i++) sums[i] += yArr[i];
  }
  return sums;
}

// ═══════════════════════════════════════════════════
// BACKGROUND SUBTRACTION
// ═══════════════════════════════════════════════════
function shirleyBackground(be, intensity, maxIter) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  let bg = new Array(n).fill(0);

  for (let iter = 0; iter < maxIter; iter++) {
    const newBg = new Array(n).fill(0);
    for (let i = 0; i < n; i++) {
      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
      // (Proctor–Sherwood): a noise channel below the background contributes
      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
      // integrated the raw difference and converged to a different fixed point,
      // 0.015–0.24 % of the span away from the background the server fits).
      let sumRight = 0;
      for (let j = i; j < n - 1; j++) {
        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      let sumTotal = 0;
      for (let j = 0; j < n - 1; j++) {
        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
      newBg[i] = I1 + (I0 - I1) * frac;
    }
    bg = newBg;
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
  for (const line of lines) {
    if (!line.trim() || line.startsWith('#') || line.startsWith('%')) continue;

exec
/bin/zsh -lc "rg -n 'bg_funcs|bg_func|bg_start|bg_end|n_avg|shirley_background\\(' fitting.py; rg -n 'computeBackground\\(|computeBgWithSettings\\(|bgIntensity|bgSubtracted|findPeaks|Find Peaks|roiHint' templates/index.html | head -180; rg --files tests/js; ls -ld venv /Users/skyefortier/xps-app/venv/bin/python3; rg --files -g '*AGENTS*' /Users/skyefortier/xps-app/.claude /Users/skyefortier 2>/dev/null | head -30" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/background_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 2678ms:
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
#   pid: 56097,
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
  duration_ms: 2675.676324
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
# duration_ms 2693.731251

 succeeded in 9763ms:
exec
/bin/zsh -lc "sed -n '4408,4437p' templates/index.html; sed -n '1590,1688p' fitting.py; sed -n '5100,5168p' templates/index.html; sed -n '9225,9375p' templates/index.html; sed -n '12460,12510p' templates/index.html; rg -n 'background|shirley|smart' tests/js/{bg_window_indices,endpoint_avg_default,find_peaks_endpoint_avg,roi_clamp_centre_warning}.test.js | head -95" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
function shirleyBackground(be, intensity, maxIter) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  let bg = new Array(n).fill(0);

  for (let iter = 0; iter < maxIter; iter++) {
    const newBg = new Array(n).fill(0);
    for (let i = 0; i < n; i++) {
      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
      // (Proctor–Sherwood): a noise channel below the background contributes
      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
      // integrated the raw difference and converged to a different fixed point,
      // 0.015–0.24 % of the span away from the background the server fits).
      let sumRight = 0;
      for (let j = i; j < n - 1; j++) {
        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      let sumTotal = 0;
      for (let j = 0; j < n - 1; j++) {
        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
      newBg[i] = I1 + (I0 - I1) * frac;
    }
    bg = newBg;
  }
  return bg;
}

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

  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
// the data in every fit, background, area and export — the defect was that
// nothing said so. This reports the window actually used; it writes nothing
// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
// the same two numbers against the same corrected energies to a server mask
// of the same inclusive form, so this one window is the one both use.
// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
function _roiWindowStatus() {
  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
  if (!corrBE.length) return { state: 'no-data' };
  let dMin = Infinity, dMax = -Infinity;
  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  const lo = parseFloat(document.getElementById('roi-min').value);
  const hi = parseFloat(document.getElementById('roi-max').value);
  const { be } = getROIData();
  let sMin = Infinity, sMax = -Infinity;
  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
  if (!be.length) return { ...base, state: 'no-overlap' };
  // one sampling step = median |Δ corrected BE|: within a step there is no
  // sample the window could have included, so a toFixed(1) rounding of an
  // edge is not "past the data" (a grid-relative criterion, not a threshold
  // on intensity)
  const d = [];
  for (let i = 1; i < corrBE.length; i++) d.push(Math.abs(corrBE[i] - corrBE[i - 1]));
  d.sort((a, b) => a - b);
  const step = d.length ? (d.length % 2 ? d[(d.length - 1) / 2] : 0.5 * (d[d.length / 2 - 1] + d[d.length / 2])) : 0;
  const past = (Number.isFinite(lo) && lo < dMin - step) || (Number.isFinite(hi) && hi > dMax + step);
  return { ...base, step, state: past ? 'past' : 'ok' };
}
function _roiHintFor(st) {
  const f = v => v.toFixed(2);
  if (st.state === 'past') return { cls: '', text: `ROI extends past your data — clipped to ${f(st.sMin)}–${f(st.sMax)} eV.` };
  if (st.state === 'inverted') return { cls: 'amber', text: 'BE min is above BE max — no data is selected.' };
  if (st.state === 'no-overlap') return { cls: 'amber', text: `ROI does not overlap your data (${f(st.dMin)}–${f(st.dMax)} eV) — no data is selected.` };
  return null;
}
function _refreshRoiHint(st) {
  const el = document.getElementById('roi-hint');
  if (!el) return;
  const h = st ? _roiHintFor(st) : null;
  if (!h) { if (el.style.display !== 'none') { el.style.display = 'none'; el.textContent = ''; } return; }
  if (el.textContent !== h.text) el.textContent = h.text;
  el.className = 'roi-hint' + (h.cls ? ' ' + h.cls : '');
  el.style.display = '';
}
// A component centred outside the selected data: the fit sees only its tail.
// Almost always a placement error — and the one way to reach the DS+G
// normalisation limit (plan 2026-09-22-dsg-page-evaluator §3c).
function _centreOutsideData(p, st) {
// (setDatasetVisibility) is index-based. Returns -1 if not found.
function _findStackDatasetIndex(chart, key) {
  if (!chart || !chart.data || !Array.isArray(chart.data.datasets)) return -1;
  return chart.data.datasets.findIndex(d => d._stackKey === key);
}

// Has-fit detection — source tab must have a non-null fitResult AND
// a non-empty peaks array. Drives whether _buildEntryRenderData is
// called and whether the legend's fit-toggle is enabled.
function _entryHasFit(entry) {
  const src = tabManager._getTab(entry.sourceTabId);
  return !!(src && src.fitResult && Array.isArray(src.peaks) && src.peaks.length > 0);
}

function _colorWithAlpha(hex, a) {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const alphaHex = Math.round(a * 255).toString(16).padStart(2, '0');
  return hex + alphaHex;
}

// Reproduce a source tab's background using its persisted ui state.
// Falls back to shirley for manual-anchor sources (see follow-up:
// "Stack view of post-load fits: support manual-anchor background
// reconstruction from persisted anchor points").
function _computeBackgroundForSource(be, inten, srcUi) {
  if (!be || !be.length || !inten || !inten.length) {
    return new Array(be ? be.length : 0).fill(0);
  }
  let settings = {
    bgType:      (srcUi && srcUi.bgType)      || 'shirley',
    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
    endpointAvg: (srcUi && srcUi.endpointAvg) || LEGACY_ENDPOINT_AVG,
    bgStart:     (srcUi && srcUi.bgStart)     || '',
    bgEnd:       (srcUi && srcUi.bgEnd)       || '',
  };
  if (settings.bgType === 'manual') settings = { ...settings, bgType: 'shirley' };
  return computeBackgroundCore(be, inten, settings);
}

// Build all render data for one entry's fit visualization:
//   { be, bg, fittedY, peaks: [{peak, y}] }
// `be` is corrected-BE space; `bg` is raw-level background curve;
// `fittedY` is the raw-level envelope; each peak's `y` is the raw-level
// peak shape (peak height + bg).
//
// Three internal paths, chosen by what the source tab has available:
//   A:  fitResult.be + fitResult.fittedY both present, lengths match
//       → use fittedY directly (already raw-level). Frozen to fit-time
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
//
// The big win: Path B (post-load) recomputes a Shirley background per
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
tests/js/endpoint_avg_default.test.js:7:// and stack Path B / re-render reconstruct the background from that value.
tests/js/bg_window_indices.test.js:2:// design, docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md,
tests/js/bg_window_indices.test.js:5:// The user types two binding energies; the preview background, the fit
tests/js/bg_window_indices.test.js:100:    'shirleyBackground', 'smartBackground', 'smartExperimentalBackground',
tests/js/bg_window_indices.test.js:101:    'shirleyLinearBackground', 'tougaardBackground', '_applyEndpointAveraging',
tests/js/bg_window_indices.test.js:104:  const unused = () => { throw new Error('unexpected background type call'); };
tests/js/bg_window_indices.test.js:110:    const out = core(be, inten, { bgType: 'linear', shirleyIter: '5', endpointAvg: '1', bgStart: s, bgEnd: e });

codex
The smart call site correctly passes the raw slice, and I found no other production callers of `smartBackground`. The bridge matches the backend’s anchor-window calls. The test run hit a Python dependency’s temporary-directory probe in this read-only sandbox; I’m checking whether an in-memory workaround will let it run. I’m also probing Shirley’s zero-signal behavior.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');

const h=new Function('\\''require'\\'','\\''__dirname'\\'',src.slice(0,src.indexOf(\"test('\\''the cases\"))+'\\''return {JS,py,jsBg,CASES,compare,extractFn,html};'\\'')(require,path.resolve('\\''tests/js'\\''));
const inputs=[
['\\''flat'\\'',[0,1,2],[5,5,5]],
['\\''two'\\'',[0,1],[5,10]],
['\\''below'\\'',[0,1,2,3,4],[10,1,1,1,20]],
['\\''nonuniform below'\\'',[0,1,3,6,10],[10,1,1,1,20]],
['\\''slope'\\'',[0,1,2,3,4],[10,12.5,15,17.5,20]],
['\\''uneven slope'\\'',[0,1,3,6,10],[10,12.5,15,17.5,20]],
['\\''negative'\\'',[0,1,2,3,4],[-10,-9,-5,-4,-2]],
['\\''peak'\\'',[0,1,2,3,4],[10,12,30,22,20]]
];
const items=inputs.flatMap(([label,be,inten])=>['\\''shirley'\\'','\\''smart'\\''].map(method=>({label,be,inten,method,n_avg:1})));
const py=h.py({mode:'\\''bg'\\'',items});
items.forEach((c,i)=>console.log(JSON.stringify({case:c.label,method:c.method,js:h.jsBg(c.be,c.inten,c.method,1),py:py[i]})));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');
new Function('\\''require'\\'','\\''__dirname'\\'',src)(require,path.resolve('\\''tests/js'\\''));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 3380ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
{"case":"flat","method":"shirley","js":[5,5,5],"py":[5,5,5]}
{"case":"flat","method":"smart","js":[5,5,5],"py":[5,5,5]}
{"case":"two","method":"shirley","js":[5,10],"py":[5,10]}
{"case":"two","method":"smart","js":[5,10],"py":[5,10]}
{"case":"below","method":"shirley","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"below","method":"smart","js":[10,1,1,1,20],"py":[10,1,1,1,20]}
{"case":"nonuniform below","method":"shirley","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"nonuniform below","method":"smart","js":[10,1,1,1,20],"py":[10,1,1,1,20]}
{"case":"slope","method":"shirley","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"slope","method":"smart","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"uneven slope","method":"shirley","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"uneven slope","method":"smart","js":[10,12.5,15,17.5,20],"py":[10,12.5,15,17.5,20]}
{"case":"negative","method":"shirley","js":[-10,-10,-6,-2,-2],"py":[-10,-8,-4,-2,-2]}
{"case":"negative","method":"smart","js":[-10,-10,-6,-4,-2],"py":[-10,-9,-5,-4,-2]}
{"case":"peak","method":"shirley","js":[10,10.407177151592373,14.7203325863296,19.31315543473723,20],"py":[10,10.407177103188474,14.720332517766131,19.313155414577658,20]}
{"case":"peak","method":"smart","js":[10,10.407177151592373,14.7203325863296,19.31315543473723,20],"py":[10,10.407177103188474,14.720332517766131,19.313155414577658,20]}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');
const baseline=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\''}); const changed=src.replace(\"fs.readFileSync(path.join(REPO_ROOT, '\\''templates/index.html'\\''), '\\''utf8'\\'')\",JSON.stringify(baseline)); new Function('\\''require'\\'','\\''__dirname'\\'',changed)(require,path.resolve('\\''tests/js'\\''));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc 'node --test tests/js/bg_window_indices.test.js tests/js/endpoint_avg_default.test.js tests/js/find_peaks_endpoint_avg.test.js tests/js/roi_clamp_centre_warning.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 121ms:
# Subtest: window at the ROI bounds covers every point, including the last one
ok 1 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 2.283042
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 2 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.2636
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 3 - bound order does not matter
  ---
  duration_ms: 1.328467
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 4 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.26549
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 5 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.246624
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 6 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.255731
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 7 - exactly two points in range is a usable window
  ---
  duration_ms: 0.244406
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 8 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 1.27166
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 9 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 0.890718
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 10 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 1.671534
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 11 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 2.181014
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 12 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 1.088216
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 13 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 1.771034
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 14 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 1.097694
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 15 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.647187
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 16 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.433549
  type: 'test'
  ...
# Subtest: runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
ok 17 - runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
  ---
  duration_ms: 1.445611
  type: 'test'
  ...
# Subtest: _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
ok 18 - _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
  ---
  duration_ms: 0.542984
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 19 - an ROI inside the data: no hint
  ---
  duration_ms: 6.827368
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 20 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 3.837555
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 21 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 2.91631
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 22 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 4.72321
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 23 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 4.281159
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 24 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 2.209666
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 25 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 2.144364
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 26 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 4.279877
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 27 - a descending acquisition behaves the same
  ---
  duration_ms: 2.185956
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 28 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 4.16658
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 29 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.658039
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 30 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.463704
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 31 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 1.820192
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 32 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 8.668331
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 33 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 4.986578
  type: 'test'
  ...
1..33
# tests 33
# suites 0
# pass 33
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 183.646912

 succeeded in 22748ms:
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
  duration_ms: 1.151402
  type: 'test'
  ...
# Subtest: shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 2 - shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2464.157779
  type: 'test'
  ...
# Subtest: shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 3 - shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2080.246663
  type: 'test'
  ...
# Subtest: smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 4 - smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2124.798531
  type: 'test'
  ...
# Subtest: smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 5 - smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2101.455322
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 6 - smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1610.606443
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 7 - smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1719.002072
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 8 - tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1630.122444
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 9 - tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1656.770507
  type: 'test'
  ...
# Subtest: linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 10 - linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1762.624059
  type: 'test'
  ...
# Subtest: linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 11 - linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1911.051205
  type: 'test'
  ...
# Subtest: KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
ok 12 - KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
  ---
  duration_ms: 1974.26568
  type: 'test'
  ...
1..12
# tests 12
# suites 0
# pass 12
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 21049.334751

 exited 1 in 22147ms:
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
  duration_ms: 1.153835
  type: 'test'
  ...
# Subtest: shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
not ok 2 - shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2404.024467
  type: 'test'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.eval (eval at <anonymous> ([eval]:5:223), <anonymous>:80:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async startSubtestAfterBootstrap (node:internal/test_runner/harness:296:3)
  ...
# Subtest: shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
not ok 3 - shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2082.776824
  type: 'test'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 2.07e-4 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.eval (eval at <anonymous> ([eval]:5:223), <anonymous>:80:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
not ok 4 - smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1931.224727
  type: 'test'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.eval (eval at <anonymous> ([eval]:5:223), <anonymous>:80:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
not ok 5 - smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2204.506497
  type: 'test'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 7.17e-3 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.eval (eval at <anonymous> ([eval]:5:223), <anonymous>:80:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 6 - smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1649.457102
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 7 - smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1572.506276
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 8 - tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1655.604525
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 9 - tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1704.285664
  type: 'test'
  ...
# Subtest: linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 10 - linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1551.565764
  type: 'test'
  ...
# Subtest: linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 11 - linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1558.527187
  type: 'test'
  ...
# Subtest: KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
ok 12 - KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
  ---
  duration_ms: 2034.536444
  type: 'test'
  ...
1..12
# tests 12
# suites 0
# pass 8
# fail 4
# cancelled 0
# skipped 0
# todo 0
# duration_ms 20362.569866

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');
const h=new Function('\\''require'\\'','\\''__dirname'\\'',src.slice(0,src.indexOf(\"test('\\''the cases\"))+'\\''return {JS,py,jsBg,CASES,compare,extractFn,html};'\\'')(require,path.resolve('\\''tests/js'\\''));

const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\''});
const oldSrc=src.slice(0,src.indexOf(\"test('\\''the cases\")).replace(\"fs.readFileSync(path.join(REPO_ROOT, '\\''templates/index.html'\\''), '\\''utf8'\\'')\",JSON.stringify(oldhtml));
const old=new Function('\\''require'\\'','\\''__dirname'\\'',oldSrc+'\\''return {jsBg};'\\'')(require,path.resolve('\\''tests/js'\\''));
const items=[];
for(let a=5;a<=25;a+=2)for(let b=5;b<=25;b+=2)for(let c=5;c<=25;c+=2) items.push({be:[0,1,2,3,4],inten:[10,a,b,c,20],method:'\\''shirley'\\'',n_avg:1});
const py=h.py({mode:'\\''bg'\\'',items});
const rows=items.map((c,i)=>{const js=h.jsBg(c.be,c.inten,c.method,1), prior=old.jsBg(c.be,c.inten,c.method,1);return {...c,js,py:py[i],old:prior,d:Math.max(...js.map((v,j)=>Math.abs(v-py[i][j]))),prevD:Math.max(...prior.map((v,j)=>Math.abs(v-py[i][j])))};}).filter(r=>r.d>0.1);
console.log('\\''divergent count'\\'',rows.length);
console.log('\\''biggest'\\'',JSON.stringify(rows.sort((a,b)=>b.d-a.d).slice(0,8)));
console.log('\\''new only'\\'',JSON.stringify(rows.filter(r=>r.prevD<0.00001).slice(0,8)));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "rg -n 'smartBackground|shirleyBackground|bgIntensity.*(equal|===)|background.*fixture' tests templates --glob '*.js' --glob '*.html'; sed -n '7350,7378p' templates/index.html; sed -n '10540,10578p' templates/index.html; sed -n '10650,10700p' templates/index.html; sed -n '3330,3475p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
templates/index.html:4408:function shirleyBackground(be, intensity, maxIter) {
templates/index.html:4438:function smartBackground(be, intensity, maxIter, rawIntensity) {
templates/index.html:4449:  const shir = shirleyBackground(be, intensity, maxIter);
templates/index.html:4613:// Completely standalone — does not call shirleyBackground / smartBackground.
templates/index.html:4748:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
templates/index.html:4749:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
templates/index.html:9319:      && fr.bgIntensity.length === fr.be.length) {
templates/index.html:9805:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
tests/js/local_lm_descent.test.js:39:  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
tests/js/background_parity.test.js:49:  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
tests/js/bg_window_indices.test.js:100:    'shirleyBackground', 'smartBackground', 'smartExperimentalBackground',
tests/js/tougaard_twin.test.js:156:  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
tests/js/tougaard_twin.test.js:157:  const smartBackground = () => { throw new Error('unexpected route: smart'); };
    co.value = graphiteFittedRaw.toFixed(3);
    cl.value = '284.50';
    if (typeof updateChargeCorrection === 'function') updateChargeCorrection();
  }

  // 5. Build state.fitResult exactly as runFit() does.
  const { be: be2, inten: inten2 } = getROIData();
  const bgI2 = computeBackground(be2, inten2);
  const bgSub2 = inten2.map((v, i) => v - bgI2[i]);
  const stats = json.statistics || {};
  const chiReduced = stats.reduced_chi_square || 0;
  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
  const roiRange = { min: _arrMin(be2).toFixed(1), max: _arrMax(be2).toFixed(1) };
  state.fitResult = {
    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
    chiReduced, rmse,
    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
    backendResult: json,
    fittedY: json.fitted_y,
    roiRange,
    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
  };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  // 6. Update the same DOM elements runFit() updates.
  const fq = document.getElementById('fit-quality');
  if (fq) {
    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
    if (typeof _CHISQ_TOOLTIP !== 'undefined') fq.setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
      ..._activeTab().modelProvenance, reportable: false, caveat: _localFitCaveat(_activeTab().modelProvenance),
    } : null),
  };
  const fname = document.getElementById('save-fname').value.trim() || 'spectrum';
  _downloadBlob(
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
    fname + '.fit.json'
  );
  notify('Fit parameters saved.', 'green');
}

// ── 2. Save Spectrum (v2) — active tab only ──────────
function _doSaveSpectrum() {
  tabManager._syncActiveToRecord();
  const tab = tabManager._getTab(tabManager.activeId);

  // Compute current curves
  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const modelFull = evalAllPeaks(be, state.peaks);
  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
  const residuals = bgSub.map((v, i) => v - modelFull[i]);
  // F1: a stale result's stored curve is the previous model's; the file's
  // fittedY then matches its residuals (the current model), as with no fit
  const _saveStats = _statsLiveState();
  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);

  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
  // for LACX with caM > 0, only the array evaluator applies the shape's
  // Gaussian convolution — evalPeak silently ignores caM. These curves
  // and areas are written into the saved .spec.json file.
  const peakCurves = state.peaks.map(p => {
    const yArr = evalPeakArray(be, p);
    return {
      id: p.id, name: p.name,
      y: yArr,
      area: yArr.reduce((sum, y, i) => {
        if (i === 0) return 0;
        const dx = Math.abs(be[i] - be[i - 1]);
  const _roundBE = (a) => Array.isArray(a) ? a.map(v => Math.round(v * 1e4) / 1e4) : null;
  const _roundIntensity = (a) => Array.isArray(a) ? a.map(v => Number(v.toPrecision(6))) : null;
  const buildTabData = (t) => {
    if (t.isStack) {
      return {
        id: t.id, name: t.name, isStack: true,
        _nextColorIdx: t._nextColorIdx || 0,
        lineWidth: t.lineWidth ?? 1.5,
        verticalOffset: t.verticalOffset ?? 0,
        entries: (t.entries || []).map(e => ({
          id: e.id,
          sourceTabId: e.sourceTabId,
          color: e.color,
          visible: !!e.visible,
          showFit: !!e.showFit,
        })),
      };
    }
    const rec = {
      id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
      rawBE: t.rawBE, rawIntensity: t.rawIntensity,
      ccShift: t.ccShift, chargeVerified: t.chargeVerified ?? true,
      peaks: t.peaks.map(p => ({...p})),
      nextId: t.nextId,
      fitResult: t.fitResult ? {
        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
        rFactor: t.fitResult.rFactor || null,   // F1: the fit's own R, not one recomputed from edited peaks on reload
        // Frozen fit grid: persisted so post-load updatePlot() renders the
        // recorded fit (haveFit path) instead of recomputing background and
        // residuals from current settings. Absent in older saves — loaders
        // fall back to reconstruction.
        be: _roundBE(t.fitResult.be),
        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
        roiRange: t.fitResult.roiRange || null,
        // Engine identity (unit A0): a local-engine result stays labelled
        // "Residual variance" after reload instead of becoming chi-square.
        engine: t.fitResult.engine || null,
        objective: t.fitResult.objective || null,
        weighting: t.fitResult.weighting || null,
        status: t.fitResult.status || null,
        starts: _startsForSave(_startsIfCurrent(t.fitResult, _startsRecordKey(t))),
        startsModelKey: t.fitResult.startsModelKey || null,
        chosenAlternative: _startsIfCurrent(t.fitResult, _startsRecordKey(t)) ? (t.fitResult.chosenAlternative || null) : null,
        iterations: t.fitResult.iterations ?? null,
        reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
        caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
        ..._statsSaveFields(_statsRecordState(t)),   // F1: judged against the RECORD's key
      } : null,
      modelProvenance: t.modelProvenance || null,
      this.activateTab(this.tabs[nextIdx].id);
    } else {
      this.renderTabBar();
    }
    this._updateSurveyPanel();
  }

  // ── Folder upload ───────────────────────────────

  async loadFolder(fileList) {
    const files = Array.from(fileList);
    if (!files.length) return;

    const eligible = this._filterFiles(files);
    if (!eligible.length) {
      notify('No XPS data files found in folder.', 'amber');
      return;
    }

    const prog = document.getElementById('folder-progress');
    prog.classList.add('active');
    let done = 0;
    const update = () => { prog.textContent = 'Loading ' + done + '/' + eligible.length + '\u2026'; };
    update();

    for (const file of eligible) {
      await this._loadOneFile(file);
      done++;
      update();
    }

    prog.classList.remove('active');
    notify('Loaded ' + done + ' spectra', 'green');
  }

  // ── Serialization ───────────────────────────────

  toJSON() {
    this._syncActiveToRecord();
    return {
      version: 2,
      timestamp: new Date().toISOString(),
      activeId: this.activeId,
      tabs: this.tabs.map(t => ({
        id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
        rawBE: t.rawBE,
        rawIntensity: t.rawIntensity,
        ccShift: t.ccShift,
        peaks: t.peaks.map(p => ({...p})),
        nextId: t.nextId,
        markedElements: t.markedElements || [],
        notes: t.notes || '',
        ui: {...t.ui},
      })),
      // v1 compat keys from active tab
      peaks: state.peaks.map(p => ({...p})),
      nextId: state.nextId,
      chargeCorrection: {
        method: document.getElementById('cc-method').value,
        observedBE: document.getElementById('cc-obs').value,
        shift: state.ccShift
      },
      background: {
        type: document.getElementById('bg-type').value,
        start: document.getElementById('bg-start').value,
        end: document.getElementById('bg-end').value,
        shirleyIter: document.getElementById('shirley-iter').value,
        endpointAvg: document.getElementById('bg-endpoint-avg').value
      },
      roi: {
        min: document.getElementById('roi-min').value,
        max: document.getElementById('roi-max').value
      }
    };
  }

  fromJSON(data) {
    if (data.version === 1 || !data.tabs) {
      // v1 backward compat: apply settings to the ACTIVE tab only
      // Other tabs are preserved — this just restores peaks/background/CC
      if (!this.activeId || !state.rawBE.length) {
        notify('Load a spectrum file first, then load the v1 setup.', 'amber');
        return;
      }
      const active = this._getTab(this.activeId);
      if (!active) return;

      // Audit F1/F4/F5: reject unsafe peak ids/links/colors before rendering.
      const pe = _peaksLoadError(data.peaks);
      if (pe) { notify('Fit not loaded: ' + pe + '.', 'red', true); return; }

      // Import is an undoable transaction on this record: the previous model
      // (and its averaging) is one Ctrl-Z away, redo is cleared, and a Find
      // Peaks result produced for the previous model no longer applies.
      pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
      active.findPeaks = null;
      // Apply peaks. Parameters imported onto this tab's data carry no verdict:
      // "not supported by the data" was about the data they were fitted to.
      state.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p, support: null})));
      state.nextId = data.nextId || (Math.max(0, ...state.peaks.map(p => p.id)) + 1);
      state.fitResult = null;
      active.peaks = state.peaks;
      active.nextId = state.nextId;
      active.fitResult = null;
      // Provenance of the imported parameters (unit A0): a model saved from
      // a local (unweighted) fit stays a starting point, not a result.
      active.modelProvenance = _isLocalProvenance(data.fitStatistics)
        ? { ...data.fitStatistics, importedFrom: 'fit.json' } : null;

      // Apply charge correction
      if (data.chargeCorrection) {
        state.ccShift = data.chargeCorrection.shift || 0;
        active.ccShift = state.ccShift;
        active.ui.ccMethod = data.chargeCorrection.method || 'none';
        active.ui.ccObs = data.chargeCorrection.observedBE || '';
      }

      // Fit loaded from external file — CC not verified for this spectrum
      active.chargeVerified = false;
      this._updateCCVerifiedUI(false);

      // Endpoint averaging is resolved whether or not the file carries a
      // background block: v1 files written before 2026-09-08 never recorded
      // it (those fits were made at 1), and an accepted peaks-only file must
      // not inherit the fresh target tab's new-tab default either (Codex
      // round 1, both runs).
      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;

      // Apply background
      if (data.background) {
        active.ui.bgType = data.background.type || 'shirley';
        active.ui.bgStart = data.background.start || '';
        active.ui.bgEnd = data.background.end || '';
        active.ui.shirleyIter = data.background.shirleyIter || '5';
        // bgSubtractedView is missing from pre-feature saves → falsy default
        active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
      }

      // Apply ROI
      if (data.roi) {
        active.ui.roiMin = data.roi.min || '';
        active.ui.roiMax = data.roi.max || '';
      }

      // Apply notes
      if (data.notes) active.notes = data.notes;

 succeeded in 5509ms:
/Users/skyefortier/.matplotlib is not a writable directory
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Lcnoxto2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Ef0cQT3f' (errno=Operation not permitted)
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
divergent count 75
biggest [{"be":[0,1,2,3,4],"inten":[10,5,5,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,7,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,9,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,11,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,5,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,7,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,9,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,11,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0}]
new only [{"be":[0,1,2,3,4],"inten":[10,5,5,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,7,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,9,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,5,11,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,5,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,7,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,9,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0},{"be":[0,1,2,3,4],"inten":[10,7,11,17,20],"method":"shirley","n_avg":1,"js":[10,10,10,15,20],"py":[10,12.5,15,17.5,20],"old":[10,12.5,15,17.5,20],"d":5,"prevD":0}]

codex
All 12 new tests pass, and running them against F3’s page produces exactly the four expected failures. I also found a new positive-count regression: for a five-point window whose interior lies below the backend’s initial baseline, the clamped JS converges to a different curve. F3 matched Python on that case. I’m checking both directions and smart’s result before assigning severity.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''background_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');
const h=new Function('\\''require'\\'','\\''__dirname'\\'',src.slice(0,src.indexOf(\"test('\\''the cases\"))+'\\''return {JS,py,jsBg,CASES,compare,extractFn,html};'\\'')(require,path.resolve('\\''tests/js'\\''));

const inputs=[{label:'\\''below initial baseline'\\'',be:[0,1,2,3,4],inten:[10,5,5,17,20]},{label:'\\''nonuniform'\\'',be:[0,1,3,6,10],inten:[10,5,5,17,20]}];
const items=inputs.flatMap(c=>['\\''shirley'\\'','\\''smart'\\'','\\''linear'\\''].flatMap(method=>[false,true].map(rev=>({...c,be:rev?c.be.slice().reverse():c.be,inten:rev?c.inten.slice().reverse():c.inten,rev,method,n_avg:1}))));
const py=h.py({mode:'\\''bg'\\'',items});
items.forEach((c,i)=>console.log(JSON.stringify({...c,py:py[i],iters:[5,50,200,201,1000].map(iter=>({iter,bg:h.JS.computeBackgroundCore(c.be,c.inten,{bgType:c.method,shirleyIter:String(iter),endpointAvg:'\\''1'\\'',bgStart:'\\'''\\'',bgEnd:'\\'''\\''})}))})));
const measurement=h.CASES.flatMap(c=>['\\''shirley'\\'','\\''smart'\\''].flatMap(method=>[1,10].map(n_avg=>({...c,method,n_avg}))));
const outs=h.py({mode:'\\''bg'\\'',items:measurement});
const rows=measurement.map((c,i)=>({label:c.label,method:c.method,n_avg:c.n_avg,...Object.fromEntries([5,200].map(iter=>[iter,Math.max(...h.JS.computeBackgroundCore(c.be,c.inten,{bgType:c.method,shirleyIter:String(iter),endpointAvg:String(c.n_avg),bgStart:'\\'''\\'',bgEnd:'\\'''\\''}).map((v,j)=>Math.abs(v-outs[i][j])))/(Math.max(...c.inten)-Math.min(...c.inten))*100]))}));
console.log('\\''measurements maxima'\\'',JSON.stringify(['\\''shirley'\\'','\\''smart'\\''].flatMap(method=>[1,10].map(n_avg=>({method,n_avg,...Object.fromEntries([5,200].map(iter=>[iter,Math.max(...rows.filter(r=>r.method===method&&r.n_avg===n_avg).map(r=>r[iter]))]))})))));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "nl -ba CLAUDE.md | sed -n '740,761p'; nl -ba tests/js/background_parity.test.js | sed -n '51,90p'; sed -n '1,140p' tests/js/local_lm_descent.test.js; sed -n '16290,16420p' templates/index.html; rg -n 'bg-type|shirley_linear' templates/index.html | head -25; git diff --check 895f323..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
   740	| `smart_exp` | Experimental Shirley variant. |
   741	| `shirley_linear` | Shirley with a linear-fallback bridge. |
   742	| `linear` | Straight line between ROI endpoints. |
   743	| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
   744	| `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |
   745	
   746	The page's background twins (`computeBackgroundCore`: what it draws, freezes
   747	into `fitResult.bgIntensity` at fit time, saves, and what the local engine
   748	fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
   749	iteration count for shirley, smart, smart_exp, tougaard and linear, with
   750	endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
   751	2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
   752	against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
   753	the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
   754	descending grids; the UI's Shirley iteration count (default 5) leaves
   755	0.016–0.019 % of the span of unfinished iteration (Part 5 of the
   756	sealed-fit-record memo).
   757	
   758	Use Shirley for standard core-level regions. Linear only when the
   759	spectral window is very narrow and featureless.
   760	
   761	## Quantification
    51	].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
    52	  '\nreturn { computeBackgroundCore };')();
    53	const CONVERGED_ITER = 200;
    54	const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
    55	  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });
    56	
    57	const CASES = py({ mode: 'cases' });
    58	const span = y => Math.max(...y) - Math.min(...y);
    59	function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
    60	function compare(method, nAvg) {
    61	  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
    62	  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
    63	}
    64	
    65	test('the cases include the committed real U 4f scan, ascending and descending', () => {
    66	  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
    67	  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
    68	});
    69	
    70	// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
    71	// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
    72	// difference between 200 JS iterations and the server's 1e-6-count stopping
    73	// tolerance.
    74	const TOL = 1e-6;
    75	for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
    76	  for (const nAvg of [1, 10]) {
    77	    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
    78	      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
    79	    });
    80	  }
    81	}
    82	
    83	test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
    84	  const rows = compare('shirley_linear', 1);
    85	  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
    86	  const desc = rows.filter(r => /descending/.test(r.label));
    87	  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
    88	    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
    89	  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
    90	});
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
  env.state.peaks = [{ ...truth, center: 284.8, fwhm: 1.5, amplitude: 5 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true);
  const p = env.state.peaks[0];
  assert.ok(Math.abs(p.amplitude - 10) < 1e-3, `amplitude ${p.amplitude}`);
    case 'lorentzian':      o.shape = 'Lorentzian'; break;
    case 'asymmetric_gl':   o.shape = 'asym-GL';
      o.glMix = 100 * (p.gl_ratio ?? 0.3); o.asymmetry = p.asymmetry ?? 0.1; break;
    case 'doniach_sunjic':  o.shape = 'DS';
      o.dsAlpha = p.alpha ?? 0.1; o.dsGamma = p.gamma_asym ?? 0; break;
    case 'ds_g':            o.shape = 'DSG_LA';
      o.laAlpha = p.alpha ?? 0.1; o.laBeta = p.beta ?? 0.3; o.laM = p.m_gauss ?? p.fwhm ?? 1; break;
    case 'la_casaxps':      o.shape = 'LACX';
      o.caAlpha = p.alpha ?? 1; o.caBeta = p.beta ?? 1; o.caM = p.m ?? 50; break;
    default:                o.shape = 'GL'; o.glMix = 100 * (p.gl_ratio ?? 0.3);
  }
  return defaultPeak(o);
}

// One-time "these are unverified" confirmation, replacing the old
// required-reviewer-name gate. Same Promise/resolver pattern as
// _showAutoFitConfirmModal/_autoFitConfirmCancel.
let _findPeaksApplyConfirmResolver = null;
function _showFindPeaksApplyConfirmModal() {
  return new Promise(resolve => {
    _findPeaksApplyConfirmResolver = resolve;
    const proceed = document.getElementById('find-peaks-apply-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
      const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
      if (r) r(true);
    };
    document.getElementById('find-peaks-apply-confirm-overlay').classList.add('open');
  });
}
function _findPeaksApplyConfirmCancel() {
  document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
  const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
  if (r) r(false);
}

async function applyFindPeaks() {
  const owner = _opOwner();              // the record this apply belongs to
  const _fpLast = _fpGetLast();          // the ACTIVE tab's own result, or nothing
  if (!owner || !_fpLast) return;
  const peaks = (_fpLast.body.peaks || []);
  if (!peaks.length) { notify('Nothing to apply — the analysis emitted no peaks.', 'amber'); return; }
  if (state.peaks.length &&
      !confirm('Replace the ' + state.peaks.length + ' peak(s) on this tab ' +
               'with the ' + peaks.length + ' suggested peak(s)? ' +
               'You can undo this.')) return;
  if (!(await _showFindPeaksApplyConfirmModal())) return;
  if (!_ownerActive(owner)) {
    // The tab changed (or closed) while the confirmation was open: the
    // suggestions belong to the tab they were produced on, so nothing is
    // written anywhere.
    notify('Apply cancelled — the tab changed while the confirmation was open.', 'amber');
    return;
  }
  // the manual path's real undo: the replaced peak list must be Ctrl-Z
  // recoverable (Codex analyze review blocker). This action also changes
  // endpoint averaging (below), so the undo entry carries the pre-apply
  // value and undo/redo restore it with the peaks.
  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
  // DURABLE provenance record: stamped on every applied peak (peak objects
  // round-trip through project save/load with extra fields intact, like
  // _rsfKey does) — no reviewer name anymore, but autoSuggested/verified
  // keep the "these came from Find Peaks and haven't been checked" fact
  // alive through save/load.
  const review = {
    autoSuggested: true, verified: false,
    method: _fpLast.method, regions: _fpLast.regions,
    winner: (_fpLast.body.diagnostics || {}).winner || null,
    at: new Date().toISOString(),
  };
  state.peaks = peaks.map((p, i) => {
    const fp = _fpPeakFromBackend(p, i);
    fp._findPeaks = review;
    return fp;
  });
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // the replaced model's provenance does not describe these peaks
  const active = tabManager.tabs.find(t => t.id === tabManager.activeId);
  if (active) active._findPeaksReview = review;
  // Find Peaks now sends the Background panel's endpoint averaging (see
  // runFindPeaks), so normally this is a no-op. It still guards preview ==
  // fit when the panel was changed between the run and the apply, or when
  // the Advanced JSON named a different value: the panel and the tab
  // record are set to what the engine actually used, with a notice.
  // (No _invalidateBgCache() here: with "fit the entire window" OFF the
  // frozen fit display must stay exactly as today — invalidating the cache
  // un-froze it, caught by test_checkbox_off_preserves_todays_cropped_behavior;
  // with it ON, state.fitResult is cleared below and the preview recomputes
  // from the panel value anyway.)
  const usedEp = (_fpLast && _fpLast.endpointAvg) || LEGACY_ENDPOINT_AVG;
  const epEl = document.getElementById('bg-endpoint-avg');
  const epChanged = !!epEl && epEl.value !== usedEp;
  if (epEl) epEl.value = usedEp;
  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited
  if (epChanged) {
    notify('Find Peaks fitted with endpoint averaging ' + usedEp + '; the Background panel was set to ' +
           usedEp + ' so the preview matches the fit.', 'amber');
  }
  // The chart FREEZES its background/fit-curve display to state.fitResult's
  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
  // branch) — a prior manual Run Fit or Auto-Fit C1s Graphite leaves this
  // set, frozen to THAT fit's own (possibly narrower) range. Applying new
  // Find Peaks peaks on top never touched it, so the chart kept showing
  // background/fit cropped to the OLD frozen range regardless of how wide
  // a window Find Peaks actually used — root cause of "fit + background
  // don't span the full selected window" (2026-07-14 bug report). Find
  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
  // proper fitResult from, so when this run used "fit the entire window,"
  // clear it instead: updatePlot() then falls back to its existing
  // unfit-preview path (getROIData() + client-side computeBackground()),
  // exactly like peaks placed manually before any Run Fit — spanning the
  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.
  // Default (unchecked) leaves state.fitResult untouched — today's
  // behavior, unchanged.
  if (_fpLast && _fpLast.fitFullWindow) {
    state.fitResult = null;
    // Clearing state.fitResult fixes the CHART (updatePlot's "haveFit"
    // branch), but the status-bar widgets (χ²ᵣ, R-factor, "ROI: ...")
    // are a SEPARATE piece of DOM state that only refreshes when
    // explicitly told to (Codex review finding, 2026-07-14: this was
    // the other half of the bug report's exact symptom — the header
    // could still read the OLD fit's stale "ROI: 278.0-290.4 eV" even
    // after the chart itself had been fixed). Reset them to the SAME
    // "no committed fit yet" state TabManager.activateTab already uses
    // when a tab has no state.fitResult, rather than inventing a new
    // convention.
    const fqEl = document.getElementById('fit-quality');
    if (fqEl) { fqEl.innerHTML = '&#967;&#178; &mdash;'; fqEl.removeAttribute('data-xps-tip'); }
    const chiEl = document.getElementById('sb-chi');
    if (chiEl) chiEl.textContent = '—';
    _updateRFactorUI(null);
    _updateROIDisplay(null);
2000:              <select id="bg-type" class="xps-tip-select" onchange="_onBgTypeChange()">
2009:                     that carry bgType 'shirley_linear' still restore, render and
2011:                <option value="shirley_linear" disabled hidden data-tip="Hybrid: a linear baseline between endpoints, plus a Shirley-like cumulative correction on top. De-listed pending scientific review — only shown for saved files that already use it.">Shirley + Linear (legacy)</option>
3393:        type: document.getElementById('bg-type').value,
3831:      bgType:      document.getElementById('bg-type')?.value || 'shirley',
3850:    set('bg-type', ui.bgType);
3874:      const needsIter = (ui.bgType === 'shirley' || ui.bgType === 'smart' || ui.bgType === 'smart_exp' || ui.bgType === 'shirley_linear');
4751:  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
4780:    bgType:      document.getElementById('bg-type').value,
5770:    // and bg-type checks.
6585:// bg-type is "none", or a fit is running. The pill's checked state
6596:// `shirley-iter` is gated when bg-type doesn't need iteration.
6603:  // unavailable (defensive: covers the moment between bg-type=none
6605:  const bgType = document.getElementById('bg-type')?.value || 'shirley';
6643:  const bgType = document.getElementById('bg-type')?.value || 'shirley';
7650:    const bgType = document.getElementById('bg-type').value;
8146:    const bgType  = document.getElementById('bg-type').value;
9844:  // returns false if bg-type is "none" even when the pill is checked.
10510:      type: document.getElementById('bg-type').value,
11693:  const bgType = document.getElementById('bg-type')?.value || '';
14481:// shirley_linear is de-listed (2026-09-03) but never deleted: the <option>
14488:  const sel = document.getElementById('bg-type');
14490:  const active = sel.value === 'shirley_linear';
14491:  const opt = sel.querySelector('option[value="shirley_linear"]');
14498:  const type = document.getElementById('bg-type').value;
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HgUlrkDj' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WxI1FSOg' (errno=Operation not permitted)

 succeeded in 7120ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
{"label":"below initial baseline","be":[0,1,2,3,4],"inten":[10,5,5,17,20],"rev":false,"method":"shirley","n_avg":1,"py":[10,12.5,15,17.5,20],"iters":[{"iter":5,"bg":[10,10,10,15,20]},{"iter":50,"bg":[10,10,10,15,20]},{"iter":200,"bg":[10,10,10,15,20]},{"iter":201,"bg":[10,10,10,15,20]},{"iter":1000,"bg":[10,10,10,15,20]}]}
{"label":"below initial baseline","be":[4,3,2,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"shirley","n_avg":1,"py":[20,17.5,15,12.5,10],"iters":[{"iter":5,"bg":[20,15,10,10,10]},{"iter":50,"bg":[20,15,10,10,10]},{"iter":200,"bg":[20,15,10,10,10]},{"iter":201,"bg":[20,15,10,10,10]},{"iter":1000,"bg":[20,15,10,10,10]}]}
{"label":"below initial baseline","be":[0,1,2,3,4],"inten":[10,5,5,17,20],"rev":false,"method":"smart","n_avg":1,"py":[10,5,5,17,20],"iters":[{"iter":5,"bg":[10,5,5,15,20]},{"iter":50,"bg":[10,5,5,15,20]},{"iter":200,"bg":[10,5,5,15,20]},{"iter":201,"bg":[10,5,5,15,20]},{"iter":1000,"bg":[10,5,5,15,20]}]}
{"label":"below initial baseline","be":[4,3,2,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"smart","n_avg":1,"py":[20,17,5,5,10],"iters":[{"iter":5,"bg":[20,15,5,5,10]},{"iter":50,"bg":[20,15,5,5,10]},{"iter":200,"bg":[20,15,5,5,10]},{"iter":201,"bg":[20,15,5,5,10]},{"iter":1000,"bg":[20,15,5,5,10]}]}
{"label":"below initial baseline","be":[0,1,2,3,4],"inten":[10,5,5,17,20],"rev":false,"method":"linear","n_avg":1,"py":[10,12.5,15,17.5,20],"iters":[{"iter":5,"bg":[10,12.5,15,17.5,20]},{"iter":50,"bg":[10,12.5,15,17.5,20]},{"iter":200,"bg":[10,12.5,15,17.5,20]},{"iter":201,"bg":[10,12.5,15,17.5,20]},{"iter":1000,"bg":[10,12.5,15,17.5,20]}]}
{"label":"below initial baseline","be":[4,3,2,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"linear","n_avg":1,"py":[20,17.5,15,12.5,10],"iters":[{"iter":5,"bg":[20,17.5,15,12.5,10]},{"iter":50,"bg":[20,17.5,15,12.5,10]},{"iter":200,"bg":[20,17.5,15,12.5,10]},{"iter":201,"bg":[20,17.5,15,12.5,10]},{"iter":1000,"bg":[20,17.5,15,12.5,10]}]}
{"label":"nonuniform","be":[0,1,3,6,10],"inten":[10,5,5,17,20],"rev":false,"method":"shirley","n_avg":1,"py":[10,12.5,15,17.5,20],"iters":[{"iter":5,"bg":[10,10,10,14.285714285714285,20]},{"iter":50,"bg":[10,10,10,14.285714285714286,20]},{"iter":200,"bg":[10,10,10,14.285714285714286,20]},{"iter":201,"bg":[10,10,10,14.285714285714285,20]},{"iter":1000,"bg":[10,10,10,14.285714285714286,20]}]}
{"label":"nonuniform","be":[10,6,3,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"shirley","n_avg":1,"py":[20,17.5,15,12.5,10],"iters":[{"iter":5,"bg":[20,14.285714285714285,10,10,10]},{"iter":50,"bg":[20,14.285714285714285,10,10,10]},{"iter":200,"bg":[20,14.285714285714285,10,10,10]},{"iter":201,"bg":[20,14.285714285714285,10,10,10]},{"iter":1000,"bg":[20,14.285714285714285,10,10,10]}]}
{"label":"nonuniform","be":[0,1,3,6,10],"inten":[10,5,5,17,20],"rev":false,"method":"smart","n_avg":1,"py":[10,5,5,17,20],"iters":[{"iter":5,"bg":[10,5,5,14.285714285714285,20]},{"iter":50,"bg":[10,5,5,14.285714285714286,20]},{"iter":200,"bg":[10,5,5,14.285714285714286,20]},{"iter":201,"bg":[10,5,5,14.285714285714285,20]},{"iter":1000,"bg":[10,5,5,14.285714285714286,20]}]}
{"label":"nonuniform","be":[10,6,3,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"smart","n_avg":1,"py":[20,17,5,5,10],"iters":[{"iter":5,"bg":[20,14.285714285714285,5,5,10]},{"iter":50,"bg":[20,14.285714285714285,5,5,10]},{"iter":200,"bg":[20,14.285714285714285,5,5,10]},{"iter":201,"bg":[20,14.285714285714285,5,5,10]},{"iter":1000,"bg":[20,14.285714285714285,5,5,10]}]}
{"label":"nonuniform","be":[0,1,3,6,10],"inten":[10,5,5,17,20],"rev":false,"method":"linear","n_avg":1,"py":[10,11,13,16,20],"iters":[{"iter":5,"bg":[10,12.5,15,17.5,20]},{"iter":50,"bg":[10,12.5,15,17.5,20]},{"iter":200,"bg":[10,12.5,15,17.5,20]},{"iter":201,"bg":[10,12.5,15,17.5,20]},{"iter":1000,"bg":[10,12.5,15,17.5,20]}]}
{"label":"nonuniform","be":[10,6,3,1,0],"inten":[20,17,5,5,10],"rev":true,"method":"linear","n_avg":1,"py":[20,16,13,11,10],"iters":[{"iter":5,"bg":[20,17.5,15,12.5,10]},{"iter":50,"bg":[20,17.5,15,12.5,10]},{"iter":200,"bg":[20,17.5,15,12.5,10]},{"iter":201,"bg":[20,17.5,15,12.5,10]},{"iter":1000,"bg":[20,17.5,15,12.5,10]}]}
/Users/skyefortier/.matplotlib is not a writable directory
measurements maxima [{"5":0.01574944167578243,"200":7.559628125769223e-10,"method":"shirley","n_avg":1},{"5":0.018921607034407893,"200":8.882704523414394e-10,"method":"shirley","n_avg":10},{"5":0.01574944167578243,"200":7.559628125769223e-10,"method":"smart","n_avg":1},{"5":0.018921607034407893,"200":8.882704523414394e-10,"method":"smart","n_avg":10}]

exec
/bin/zsh -lc "sed -n '90,160p' tests/js/local_lm_descent.test.js; rg -n \"test\\(\" tests/js/local_lm_descent.test.js; sed -n '14478,14502p' templates/index.html; rg -n 'fitResult.*data|fitResult:|bgIntensity' templates/index.html | tail -35; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
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
  env.state.peaks = [{ ...truth, center: 284.8, fwhm: 1.5, amplitude: 5 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true);
  const p = env.state.peaks[0];
  assert.ok(Math.abs(p.amplitude - 10) < 1e-3, `amplitude ${p.amplitude}`);
  assert.ok(Math.abs(p.center - 285.0) < 1e-4, `center ${p.center}`);
  assert.ok(Math.abs(p.fwhm - 1.2) < 1e-3, `fwhm ${p.fwhm}`);
  assert.ok(out.iterations > 1, 'a real descent takes more than one accepted step');
});

test('acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', center: 284.8, fwhm: 1.5, amplitude: 5, glMix: 50, asymmetry: 0 }];
  const previousFit = { chi: 123, chiReduced: 1.5, marker: 'previous' };
  env.state.fitResult = previousFit;
  const before = JSON.stringify(env.state.peaks);
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0), { maxIterations: 1 });
  assert.equal(out.success, false, 'one iteration cannot converge from this start');
  assert.equal(JSON.stringify(env.state.peaks), before, 'peaks untouched on non-convergence');
  assert.strictEqual(env.state.fitResult, previousFit, 'previous fit result retained on non-convergence');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' || n.kind === 'amber'), 'user is told the local fit did not converge');
});

27:  const start = lines.findIndex(l => re.test(l));
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
485:test('the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom', () => {
517:  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
540:  test(`round-2 reproducer converges with m unlocked (m is held) — ${c.label}`, () => {
552:test('recovery from an amplitude of exactly zero (the new floor is not a trap)', () => {
564:test('the local engine refuses a model with no degrees of freedom; one more point and it fits', () => {
  if (tab) tab.manualAnchors = arr;
}

// shirley_linear is de-listed (2026-09-03) but never deleted: the <option>
// stays in the DOM disabled + hidden so a saved file can still restore it.
// While it IS the selected type (reachable via a restored tab.ui, or via
// batch propagation from such a tab — the dropdown-only de-listing does not
// police propagation), show it and the explanatory note; the moment any
// other type is chosen, hide both again so it cannot be newly selected.
function _syncLegacyBgOption() {
  const sel = document.getElementById('bg-type');
  if (!sel) return;
  const active = sel.value === 'shirley_linear';
  const opt = sel.querySelector('option[value="shirley_linear"]');
  if (opt) { opt.disabled = !active; opt.hidden = !active; }
  const note = document.getElementById('bg-legacy-note');
  if (note) note.style.display = active ? 'block' : 'none';
}

function _onBgTypeChange() {
  const type = document.getElementById('bg-type').value;
  _syncLegacyBgOption();
  // Toggle manual controls
  const mc = document.getElementById('manual-bg-controls');
  if (mc) mc.style.display = type === 'manual' ? 'block' : 'none';
8094:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
8139:  const bgIntensity = computeBackground(be, inten);
8140:  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
8263:                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
8305:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
8466:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
8476:      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
8477:      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
8483:  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
8814:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
9274://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
9276://   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
9318:      && Array.isArray(fr.bgIntensity)
9319:      && fr.bgIntensity.length === fr.be.length) {
9322:    bg = fr.bgIntensity.slice();
9804:                     Array.isArray(state.fitResult.bgIntensity) &&
9805:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
9811:  const plotBG = haveFit ? state.fitResult.bgIntensity
10558:  const bgIntensity = computeBackground(be, inten);
10560:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
10565:  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);
10616:    background: bgIntensity,
10674:      fitResult: t.fitResult ? {
10683:        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
11048:        peaks: [], nextId: 1, fitResult: null,
11065:      fitResult: t.fitResult || null,
11239:  const bgIntensity = computeBackground(be, inten);
11251:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
11256:      be[i].toFixed(4), inten[i].toFixed(2), bgIntensity[i].toFixed(2),
11816:    const bgI = fitResult.bgIntensity;
14262:    fitResult: {
14266:      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
14388:  _historyPreview = { snapId, peaks: snap.peaks, fitResult: snap.fitResult };
16388:  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
16395:  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AemWjOtv' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LBHmefk9' (errno=Operation not permitted)
?? docs/autofit/codex/background_twins_verdict_runA.md
?? docs/autofit/codex/background_twins_verdict_runB.md

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/local_lm_descent.test.js tests/js/batch_propagation.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 6168ms:
# Subtest: source ROI overwrites a different target ROI during propagation
ok 1 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 0.80428
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 2 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.168049
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 3 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.125066
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 4 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.125797
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 5 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.18062
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 6 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 0.655413
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 7 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 1.110964
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
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
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 8 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1339.161829
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 9 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 276.951901
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 10 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.349047
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 11 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 8.925587
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 12 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 12.66758
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 13 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 8.988179
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 14 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.984005
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 15 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.720045
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 16 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 41.795237
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 17 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.53518
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 18 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.231329
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 19 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 12.089437
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 20 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.680086
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 21 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.463213
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 22 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.124525
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 23 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1372.098494
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 24 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 59.009078
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 25 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 20.735393
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 26 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 12.668896
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 27 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 73.198116
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 28 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1274.246916
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 29 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 21.281794
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 30 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 10.78175
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 31 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.461032
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 32 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1343.454587
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 33 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 24.740133
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 34 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 22.202473
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 35 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 20.509505
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 36 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.565096
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 37 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 9.047227
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 38 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.2837
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 39 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 25.077299
  type: 'test'
  ...
1..39
# tests 39
# suites 0
# pass 38
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6224.756244

exec
/bin/zsh -lc "sed -n '418,428p' tests/js/local_lm_descent.test.js; sed -n '455,472p' tests/js/local_lm_descent.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
    const be = grid(280, 281, 0.05);
    const data = be.map(x => dataAmp * env.gaussian(x, center, 2.0));
    env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center, fwhm: 2.0, amplitude: 1, fixCenter: true, fixFwhm: true }];
    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
    if (out.success) assertConstrainedStationary(env, be, data, 1e-6, `tiny residual centre ${center}`);
  }
});

// ── Codex round-5 reproduction (2026-09-15): the certificate scale must not read a stale working width ──
test('round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one', () => {
  const env = makeEnv();
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),cp=require('\\''child_process'\\'');
const originalExec=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(args&&args[0]&&args[0].endsWith('\\''local_lm_server_parity_backend.py'\\''))return originalExec(file,['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args],opts);return originalExec(file,args,opts);};
const src=fs.readFileSync('\\''tests/js/background_parity.test.js'\\'','\\''utf8'\\'');
require(path.resolve('\\''tests/js/local_lm_descent.test.js'\\''));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "sed -n '1,30p' tests/js/local_lm_server_parity_backend.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
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

 succeeded in 9226ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 1 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1531.152245
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 2 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 302.808862
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 3 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 16.298362
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 4 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 11.274763
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 5 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 14.537497
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 6 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 11.596101
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 7 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 11.761663
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 8 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 13.323042
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 9 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 52.846666
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 10 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 29.747244
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 11 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 11.129913
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 12 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 15.875244
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 13 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 15.652327
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 14 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 11.469865
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 15 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 12.238805
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 16 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1571.631217
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 17 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 93.060589
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 18 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 27.710326
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 19 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 17.205626
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 20 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 85.962754
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 21 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1178.56913
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 22 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 30.915049
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 23 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 12.783459
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 24 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 10.647542
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
ok 25 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 4005.567343
  type: 'test'
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 26 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 23.719032
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 27 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 26.813206
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 28 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.46728
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 29 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.664477
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 30 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 9.268588
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 31 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.264736
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 32 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 24.622537
  type: 'test'
  ...
1..32
# tests 32
# suites 0
# pass 32
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
76,060
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
