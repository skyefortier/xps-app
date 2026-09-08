# Endpoint averaging: what should the default be? (investigation — no code)

Status: MEASUREMENT REPORT for the owner's decision. Nothing in the app is
changed by this document. Owner's framing (2026-09-03): a single edge point
moving a reported graphite fraction by 6 pp is a reproducibility defect —
the third measurement of the same fragility (ROI edge on a peak tail ≈ 30 %
net-area swing; n_avg 1 vs 10 ≈ 3.1× net-area scatter under Poisson noise;
1c's one-point window change ≈ 6 pp graphite at n_avg = 1). Endpoint-
anchored backgrounds are single-point sensitive and the default n_avg = 1
maximises it. Question: where does the sensitivity flatten, what does
averaging cost when the endpoint sits on a genuine slope, and what should
the default be.

Reproduce: `scripts/endpoint_avg_sensitivity.py` (append-only JSONL,
resumable) and `scripts/endpoint_avg_summarize.py`; raw rows and the printed
tables are committed under `docs/autofit/inventory/endpoint_avg/`. Data: the
committed `1-GTA UCl4-graphite … .proj.zip`, tabs `C1s Scan` (shirley, 191-pt
window inside the ROI, stored 6-component model) and `U4f Scan_0` (smart,
350-pt window = ROI, 2 × LACX + 2 × Voigt). Windows as unit 1c sends them
(inside-range inclusive), session grid at upload precision, `least_squares`.

## How `n_avg` works (for the reader)

`_apply_endpoint_averaging` replaces the first and last `cap` points of the
background window by their mean, `cap = min(n_avg, window_length // 4)`;
Shirley/Smart/Tougaard read their two anchor levels from those means. The
same convention runs in the JS preview and the backend (audit F3, 2026-07).
So `n_avg` trades one raw channel for the mean of `n` channels at each edge.

## Measurement 1 — one-point edge sensitivity ("two students one pixel apart")

Refit with the low-BE window edge moved one grid point inward, two inward,
and (C1s only, the window is inside the ROI) one outward; report the largest
change in any component's atomic fraction relative to the 1c window.

| n_avg | C1s: max Δfraction | C1s χ²ᵣ at 1c window | U 4f: max Δfraction | U 4f χ²ᵣ |
|---|---|---|---|---|
| 1 (today's default) | **6.17 pp** | 4.97 | 0.23 pp | 1.93 |
| 3 | 1.31 pp | 3.88 | 0.19 pp | 1.96 |
| 5 | 1.28 pp | 3.88 | 0.05 pp | 2.10 |
| 10 | 1.76 pp | 4.53 | 0.04 pp | 2.05 |
| 20 | 0.25 pp | 6.10 | 0.00 pp | 2.00 |

Sensitivity flattens at n_avg = 3–5: a factor ~5 on C1s (6.2 → 1.3 pp) and
~5 on U 4f (0.23 → 0.05 pp). The non-monotonic 1.76 pp at n_avg = 10 on C1s
is the slope bias below coupling to a two-point edge move. The C1s graphite
fraction at n_avg = 1 moves +3.7 / +4.2 / +6.2 pp for a 1-in / 2-in / 1-out
edge move; at n_avg = 5 the same moves are −0.1 / −1.2 / +1.3 pp.

## Measurement 2 — Poisson scatter (C1s, 24 seeded draws of the raw counts)

| n_avg | σ(graphite fraction) | σ(Adv. C 1 fraction) | mean χ²ᵣ | σ(χ²ᵣ) |
|---|---|---|---|---|
| 1 | 2.70 pp | 1.38 pp | 5.94 | 1.00 |
| 3 | 1.95 pp | 1.08 pp | 4.97 | 0.54 |
| 5 | 1.74 pp | 0.98 pp | 4.87 | 0.50 |
| 10 | 1.15 pp | 0.74 pp | 5.47 | 0.31 |
| 20 | 0.31 pp | 0.33 pp | 7.07 | 0.28 |

All 120 fits converged. The scatter keeps falling with n_avg, but from
n_avg = 10 the fit itself gets WORSE (mean χ²ᵣ 4.87 → 5.47 → 7.07): the
anchor is becoming precise about the wrong level. That is the bias.

## Measurement 3 — the cost: bias when the endpoint sits on a genuine slope

Anchor level actually used (mean of `cap` points) versus the local linear
trend evaluated AT the edge (20-point fit). For a mean over `cap` points on
a slope of `s` counts per channel the expected bias is `s·(cap−1)/2`.

| tab / edge | slope (counts / channel) | local noise σ | bias n=1 | n=3 | n=5 | n=10 | n=20 |
|---|---|---|---|---|---|---|---|
| C1s low-BE (279 eV) | 14.6 | 35 | +64 (noise) | +15 | +20 | **+59** | **+138** |
| C1s high-BE (298 eV) | −1.9 | 72 | +108 (noise) | +41 | +3 | +17 | +18 |
| U 4f high-BE (405 eV) | 5.8 | 63 | −85 (noise) | −1 | −6 | −20 | **−55** |
| U 4f low-BE (370 eV) | 2.8 | 74 | +43 (noise) | +66 | +3 | +18 | +26 |

Reading: at n_avg = 1 the "bias" column is just the raw channel's noise
(±1–1.5 σ here — this IS the single-point fragility). At n_avg = 3–5 the
anchor sits within the local noise of the trend at every edge measured. At
n_avg = 10 the slope bias reaches the noise level on the steepest edge
(C1s low-BE, 14.6 counts/channel) and at n_avg = 20 it is 2–4 × noise on
both sloped edges — which is exactly where χ²ᵣ deteriorates in
Measurements 1 and 2. Rule of thumb that falls out: keep `s·(n−1)/2` below
the local noise σ; for the slopes seen on real lab data (3–15 counts per
channel at 0.1 eV) that permits n_avg ≈ 5 comfortably, 10 marginally, 20
not.

## Caveat on the Δfraction column (owner, 2026-09-03)

The C1s max-Δfraction column is non-monotonic (1.28 pp at n = 5, 1.76 at
10, 0.25 at 20): differences of that size between adjacent n_avg values
are comparable to the measurement's own noise (one spectrum, one edge
move), so they must not carry the argument on their own. The Poisson
scatter column is clean and monotonic and is the primary evidence; the
edge-move column establishes the size of the n = 1 fragility (6.2 pp) and
that it collapses by n = 3, nothing finer than that.

## Recommendation (decided by the owner: n_avg = 3)

**Default `n_avg = 3`**, not 5. Reasoning:

- C1s χ²ᵣ is identical at 3 and 5 (3.88 at both), and the C1s one-point
  sensitivity is effectively identical (1.31 vs 1.28 pp — 3 captures 99 %
  of the available benefit).
- U 4f χ²ᵣ degrades less at 3 (1.96 vs 2.10).
- By the bias formula `s·(cap−1)/2`, the n = 3 anchor bias is HALF that of
  n = 5. Bias grows linearly with `cap` and, unlike noise, is hard to see
  in a residual; the smallest averaging that captures most of the benefit
  is the right default.
- Scatter reduction is smaller at 3 than at 5 (2.70 → 1.95 vs → 1.74 pp);
  that is the accepted price for halving the bias.

Consequences: changes numbers for NEW fits only — every saved tab carries
its own `endpointAvg` and restores it, and files that predate the field
were fit at 1 and must keep restoring as 1. Needs a one-paragraph user
note (nothing previously reported changes), and its own Codex-reviewed
unit. It does not close the fragility — a one-channel edge move at n = 3
still shifts C1s graphite by up to 1.3 pp — it reduces it to the level of
the Poisson scatter, the honest floor for a single-scan fit.

## Follow-up unit (logged 2026-09-08, from the default-3 Codex round 1): Find Peaks honours the panel's endpoint averaging

`runFindPeaks` never sends `endpoint_avg`, and `autofit/engine.py` calls
`_compute_background(x, y, bg)` at its default of 1 in three places
(candidate fitting ~880, proposal augmentation ~2196, detection ~2605), so
Find Peaks fits at 1 whatever the Background panel says. The default-3 unit
closes the visible mismatch honestly — `applyFindPeaks` sets the panel and
the tab record to the value the engine actually used and says so — but the
engine still cannot express the panel value. The real fix threads
`endpoint_avg` the way `fit_full_window` already is: the frontend payload
(`options.endpoint_avg` from `#bg-endpoint-avg`); `app.py`'s
`_ANALYZE_METHODS` defaults; each method's own `_ALLOWED_OPTIONS`
whitelist in `autofit/methods/{least_squares,ic_model_comparison,
bayesian_exchange_mc,sparse_map,max_entropy,multivariate_mcr}.py`
(unknown keys → 400); the engine
signatures `compare_models`, `fit_candidate`, `run_stability_analysis`,
`_attempt_proposal`, `_bound_fixed_refit`, `_apply_decisive_override` and
the detection call in `engine.py`; and the two direct
`_compute_background` calls outside the engine,
`autofit/methods/bayesian_exchange_mc.py` (~348) and
`autofit/methods/sparse_map.py` (~198). Default 1 keeps the parity
fixtures byte-stable. Own branch, Codex ×2, and its own line in the user
note when it ships.
