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

## Recommendation

**Default `n_avg = 5`** (the `window//4` cap already protects short windows;
the 46-point B 1s windows in the committed projects would get cap 11, so 5
applies unclipped everywhere in the corpus).

- Removes ~80 % of the one-point edge sensitivity on both spectra
  (6.2 → 1.3 pp; 0.23 → 0.05 pp) and ~35 % of the Poisson scatter.
- Bias stays inside the local noise on every measured edge, and χ²ᵣ
  improves on C1s (4.97 → 3.88). Cost to state honestly: U 4f χ²ᵣ rises
  1.93 → 2.10 at n_avg = 5 (1.96 at 3), with fractions moving < 0.1 pp —
  the smart background's raw-data clamp interacting with the averaged
  anchor at the high-BE edge; small but not zero.
- 3 would be the conservative alternative (same C1s sensitivity, smaller
  U 4f χ²ᵣ cost, less scatter reduction). 10 buys scatter at the price of
  a bias that equals the noise on steep edges; 20 is not defensible.

Consequences if adopted: changes numbers for NEW fits only (saved fits
carry their own `endpointAvg` in `tab.ui` and restore it), so it needs its
own user note but no migration; auto-fit and batch propagation read the
same field. It does not close the fragility — a one-channel move at
n_avg = 5 still shifts C1s graphite by up to 1.3 pp — it reduces it to the
level of the Poisson scatter, which is the honest floor for a
single-scan fit. Not decided here; the owner asked to see the measurements
before any default changes.
