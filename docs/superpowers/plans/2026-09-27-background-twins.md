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

## 4. Codex rounds

(filled in as they run)
