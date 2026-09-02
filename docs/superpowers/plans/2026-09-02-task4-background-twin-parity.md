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
