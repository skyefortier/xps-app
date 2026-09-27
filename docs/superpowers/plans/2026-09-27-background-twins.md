# Unit 4 — the background twins: two JS fixes and a pinned parity test (2026-09-27)

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
| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg` from a ZERO start, with an index-linear fraction when the integral vanishes: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | fitting.py's iteration OPERATION FOR OPERATION (Codex rounds 1–2): an ascending copy; numpy's linspace start (`k·step + start`, last point pinned exactly to the high-BE endpoint); `max(y − B, 0)`; the cumulative integral from the high-BE end; `b_high + ((b_low − b_high)·cum)/total` in that order; the background KEPT when no net signal is left; the 1e-6 stop; flipped back. One O(n) integral per iteration (was O(n²)). Finite inputs (NaN / Infinity not mirrored). |
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


**Round 2 — NO-GO ×2** (`background_twins_r2_verdict_run{A,B}.md`; both
confirmed the round-1 test fails on cbf3058 and the measurements):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: the straight-line start `I0 + (I1 − I0)·i/(n−1)` ended a rounding step OFF the endpoint (0.19999999999999996 for 0.2); the tiny endpoint residue became the whole integral and moved the curve by 50 % of the span on decimal data (`[1.1,0.5,0.2]` → `[1.1,1.1,0.2]`, fitting.py `[1.1,0.65,0.2]`), and the descending form differed from the ascending one | the JS now mirrors fitting.py operation for operation on an ascending copy (row S4), numpy's linspace included (last point pinned); six decimal cases in both directions added to the below-baseline parity test (which fails on f543afa's page) |
| — | (not a finding) run B's validation note: NaN / Infinity behaviour differs from Python, so the equivalence is for finite inputs | CLAUDE.md says "finite inputs" |

**Round 3 — NO-GO ×2** (`background_twins_r3_verdict_run{A,B}.md`; both
confirmed the round-2 decimal regression fails on f543afa):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: with endpoint averaging the page summed the endpoint values SEQUENTIALLY, numpy PAIRWISE; one rounding step in a mean (0.1 → 0.09999999999999999) left a residue the iteration turned into a different fixed point — run A (repeated energies, eight 0.1 / eight 3.2 endpoints) 62.5 % of the span for Shirley, 21.9 % for smart; run B (44 decimals, not converged by 200 iterations) 62.7 %; both directions, every iteration count. The round-2 tests all ran at averaging 1 | `_npMean` = numpy's `pairwise_sum` operation for operation (sequential below 8 values, eight running sums to 128, halves above), checked bit-equal to numpy 2.4.4 on 909 arrays of 1–4097 values; `_applyEndpointAveraging` uses it. Tests: both reproducers in both directions for shirley / smart / smart_exp / tougaard at averaging 10 and 1, 5, 50, 200 iterations, with fitting.py at the SAME cap (bridge takes `n_iter`); `_npMean` bit-equal to `np.mean` on 302 arrays; a randomised test at averaging 1, 3 and 10 with flat decimal endpoint runs and repeated energies. On 7de5f2b's page the reproducer test fails (62.5 %) |
| — | FOUND BY THAT RANDOMISED TEST (not in the verdicts): the page's `smart_exp` was 1.4 % of the span from fitting.py at EVERY averaging, 22 of 200 random spectra over 1e-6 — it stopped at a change of 1e-4 where fitting.py stops at 1e-6, and did not flip a descending grid (fitting.py works on an ascending copy); the fixed cases had passed at 1e-6 by luck of their shape. `smart_exp` is offered ("Smart (experimental)") | `smartExperimentalBackground` mirrors `smart_experimental_background` operation for operation (ascending copy, `_npMean` endpoints over the ascending order, numpy's linspace start, 1e-6 stop, flipped back) — the round-2 Shirley pattern. smart_exp added to the below-baseline test. After the fix: shirley, smart and smart_exp EXACTLY equal (0 difference) on all 200 × 3 averagings, tougaard ≤ 5e-15 of the span |

Suite at the round-3 fix: JS 482 tests, 480 pass, 2 todo (by design);
pytest below. Round 4 is the last allowed round.
