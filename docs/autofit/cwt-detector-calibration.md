# CWT ridge detector — synthetic calibration record

*Candidate-generation fix, 2026-07-10.  Generator:
`scripts/calibrate_cwt_detector.py` → `docs/autofit/inventory/cwt_calibration.jsonl`
(append-only, keyed, resumable).  Detector: `autofit/candidates.py`.*

## Anti-overfit contract

Every detector tunable was frozen from the SYNTHETIC batteries below
**before** the real ds7/ds8 scans were evaluated.  The real scans are
held-out confirmation only (`tests/autofit/test_candidate_pool_real_gate.py`)
and were never a tuning target.  The audit that motivated the fix
identified failure MODES (no-local-max shoulders; resolved close pairs
discarded by blunt duplicate suppression); the synthetic cases replicate
those modes as classes, not the real spectra's energies.

## Detector design

Ricker (Mexican-hat) CWT on RAW counts with ridge linking (Du, Kibbe & Lin
2006 style: largest scale downward, 1-row gap tolerance, ridges may start
at any scale — shoulder ridges only exist near their own width).  Gate
statistic: **prominence-z** — the coefficient local-max prominence divided
by the Poisson-propagated coefficient σ = sqrt((w² ∗ y)).  Design
properties, each with a measured motivation:

- **Raw counts, not background-subtracted.**  The kernel is exactly
  zero-mean and symmetric, so constant AND linear backgrounds cancel
  identically.  Measured: running the detector on Shirley-subtracted
  peakless negatives false-fires at prom_z 10–800 (the background
  algorithm's own bridging artifacts become curvature); raw negatives stay
  below ~9–12.
- **Prominence, not absolute coefficient.**  A shoulder rides the main
  peak's d² tail, where the absolute coefficient can be negative; the
  prominence measures the local curvature ANOMALY and is offset-invariant.
  Measured on the sep 0.9×FWHM / ratio 0.3 class: absolute-coefficient
  gating 0/5, prominence-z gating 5/5.
- **Per-scale edge margins** (kernel radius + 2): 'same'-convolution
  zero-padding produced exactly 2 false ridges per spectrum at z≈52
  before; 0 after.
- **Ridge length is NOT a noise gate** (measured: pure-noise ridges
  persist to length 8 under scale-correlated smoothing); min length 2 is
  kept only as a single-row-fluke guard.

## Frozen tunables (all UNVERIFIED; surfaced in every payload)

| constant | value | grounds |
|---|---|---|
| `CWT_PROM_Z_MIN` | 7.0 | H0 battery below: above q95, per-spectrum FP 3.7%; every target regime ≥ 8.5 |
| `CWT_FWHM_MIN_EV` / `MAX_EV` | 0.3 / 2.4 | below any practical XPS instrumental width ↔ just above `FWHM_MAX_ORDINARY_EV` (2.0) |
| `CWT_N_SCALES` | 8 | geometric ladder over that range |
| `CWT_SIGMA_MIN_PTS` | 2.0 | kernel sampling floor (structural) |
| `CWT_MIN_RIDGE_LENGTH` / `GAP_MAX` | 2 / 1 | standard ridge-linking practice (structural) |
| `POOL_LOCAL_MAX_MIN_SNR` | 2.0 | pool-entry floor: pure-noise smoothed maxima sit at ~0.45 |

Seeding gates reuse the reviewed F1 constants unchanged
(`PRESEED_MIN_FRACTION_OF_MAX` 0.25, `PRESEED_AMPLITUDE_SNR` 5.0,
`PRESEED_MAX` 2, coincidence dedup `PROPOSAL_COINCIDENCE_BE` 0.5).

## H0 false-positive battery (600 peakless spectra)

flat / linear-drift / sigmoid-step backgrounds × counts 100–50 000 ×
grid steps 0.05/0.1 eV, 25 seeds each.  Per-spectrum **max** prom_z:
q95 = 6.70, q99 = 8.70, max = 11.59.

| z_min | per-spectrum FP rate (pool level) |
|---|---|
| 6.5 | 6.3 % |
| **7.0 (frozen)** | **3.7 %** |
| 7.5 | 2.7 % |
| 8.0 | 1.7 % |

These are POOL-level rates (a false pool entry is tolerated by design —
the pool is overcomplete).  SEEDING-level false positives are separately
pinned at zero on the negative classes (`test_candidate_pool.py::
test_pool_zero_seeds_on_negatives`, `test_cwt_detector.py` negatives, and
the end-to-end peakless-step no-hallucination test) — the compound gate
(prom_z AND out-of-grammar AND 5× SNR AND 0.25 fraction-of-max) is what a
seed must pass.  The heavy H0 tail is concentrated in the
high-count sigmoid-step class, whose step curvature is real signal in the
curvature sense; such entries fail the seeding gates.

## Sensitivity envelope (detected/5 draws at the frozen gate; * = the
composite has NO local maximum, i.e. invisible to local-max detectors)

height 40 000 (counts at main):

| sep×FWHM | r=0.10 | 0.15 | 0.20 | 0.30 | 0.50 |
|---|---|---|---|---|---|
| 0.7 | 0* | 0* | 0* | 0* | 0* |
| 0.9 | 0* | 0* | 1* | **5*** | **5*** |
| 1.1 | 0* | **5*** | **5*** | **5*** | 5 |
| 1.3 | **5*** | **5*** | **5*** | 5 | 5 |

height 2 000: the envelope shifts one step right/up (e.g. 0.9/0.30 → 1/5,
1.1/0.30 → 5/5) — counting statistics, as designed.

Guaranteed-detection envelope claimed by the layer: **sep ≥ 0.9×FWHM at
ratio ≥ 0.3 (high counts), sep ≥ 1.1×FWHM at ratio ≥ 0.15**.  Below it,
features are honestly at/under the counting-statistics detectability
boundary and remain residual-proposal territory.  Close doublets: both
members detected 5/5 at ≥ 0.9×FWHM separation (3/5 at 0.7).  Broad-peak
splitting: 0 spurious off-center features across 20 draws.

## Held-out confirmation (real data; never tuned against)

With the constants frozen as above, the detection bar passed on ALL
targets on first evaluation (2026-07-10, `test_candidate_pool_real_gate.py`):
ds7/Scan_1 seeded at 279.32 eV (prom_z 42), ds7/Scan_5 at 280.82 (42),
ds8/Scan at 278.62 (27), ds8/Scan_0 at 278.72 (26), ds8/Scan_2 at 278.62
(55) — margins 3.7–7.9× the gate; and the 7 scans WITHOUT the class
feature gained zero curvature seeds (two-sided check).
