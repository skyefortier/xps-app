# Find Peaks: what is not scale-invariant, and Scan_6 (2026-09-28)

Owner's questions before deploying the noise-floor unit (`fix-occupancy-f-test`):
(1) why a ×0.1 rescale changes Find Peaks' result on 6 of 8 real C 1s scans
(2 of 8 on main), whether the app knows intensity units or dwell time;
(2) whether Scan_6's move from MG2 to AG2 is intended. Probe:
`scripts/findpeaks_scale_toggles.py` (8 committed C 1s scans, gate options:
4 candidates, 4 refits, proposals off); refit record:
`scripts/findpeaks_scan6_refits.py`. Raw outputs in this folder
(`tog_{M,F}_{A,C,D,E}.jsonl`: M = main's engine, F = this branch; A = budgets
off, C = + detection off, D = + background exactly scaled, E = budgets off +
background scaled, detection on).

## 1. Which sites break ×1 vs ×0.1 (runs whose winner or tier differs)

| toggles | main | this branch |
|---|---|---|
| none (as shipped) | 2 / 8 | 6 / 8 |
| wall-clock budgets off | 2 | 4 (Scan_6, UCl4 Scan_3 fixed) |
| + detection layer off | 1 (Scan_8 fixed) | 2 (Scan_8, 1-GTA Scan_2 fixed) |
| + background exactly scaled | 1 (a different scan, Scan_5) | **0** |

The three sites:

1. **Wall-clock budgets** (`CANDIDATE_TIMEOUT_SEC` 25 s shared by a
   candidate's primary fit and its stability refits; `TOTAL_ANALYSIS_TIMEOUT_SEC`
   240 s). They decide how many refits run, hence persistence. This is not a
   scale effect: it is MACHINE LOAD. On an idle i9 today main and this branch
   both give AG2 on Scan_6 (MG2 gets 3 of 4 refits: 19.9 s / 19.6 s); in the
   earlier probe main got its fourth refit and picked MG2. Find Peaks' answer on
   real data depends on how busy the server is.
2. **Detection layer** (preseed / candidate pool: Poisson signal-to-noise gates
   such as `POOL_LOCAL_MAX_MIN_SNR`, the CWT prominence z-score): SNR under
   √y falls by √10 at ×0.1 — 5 preseeded features at ×1, 4 at ×0.1.
3. **Shirley background** (`fitting.shirley_background`, stop when the change
   is < 1e-6 COUNTS — absolute): at ×0.1 it stops at a background that is not
   exactly 0.1 × the ×1 one; on Scan_7 that alone moved the promoted refit off
   a width bound.

Not causes, measured: the Poisson weight floor `max(y, 1)` (inactive — the
lowest channel at ×0.1 is 39.8 on these scans); MINPACK tolerances (relative;
every refit ends on `xtol`, ier 2); start values and bounds (scale with the
data; their `max(…, 1.0)` floors never bite here); a single fit (χ² scales by
0.1000, identical boundary hits).

**Amplifier (not scale-specific):** 14 of 36 sampled stability refits end on
`xtol` after ~30 evaluations and count as converged far from the minimum
(Scan_7 MG2: χ²ᵣ 37.6 while the best refit reaches 5.21); a refit that hits
the 18 000-evaluation cap counts as not converged even at a χ² as good as the
converged ones. Persistence is computed over attempted refits, so outcomes hinge
on rounding-level differences: toggles are not additive (main with all three
off still differs on 1 scan; this branch with budgets off + background scaled
but detection on differs on a scan none of the other combinations flipped).

*Correction (unit A1, 2026-09-29):* the Scan_7 "37.6 vs 5.21" is not a refit
stopped far from ITS minimum. Carried to convergence (the A1 certificate) it
ends at χ² 5166, a genuine constrained local minimum in a worse basin than the
5.21 one — two basins, not early stopping. The ~30-evaluation "convergence"
itself was the warm restart at the cap stall point, removed in A1
(`docs/findings/fit-termination-scope/README.md`).

**This unit's own effect**, deterministic (budgets off, detection on): main and
this branch differ on 3 of 16 runs (1-GTA Scan_2 and 8-JT Scan_7 ×1: MG2 → MG3
through the absent-slot BIC* adjustment; 8-JT Scan_5 ×0.1: tier). The earlier
"6 of 16" table in the plan mixed load-dependent budget effects into it.

## 2. Units and dwell time

The app never reads either. It hard-codes the axis label "Intensity (counts/s)".
The committed Thermo files: the Avantage chart XML labels the axis
"Counts / s"; every VGD sampled stores `DwellTime` 0.05 s and `Scans` 4
(property ids 305 / 306 in the property stream; `vgd_parser.py` ignores them).
Nominal exposure per channel t = 0.2 s.

If y is a rate, var(y) = y / t_eff. The measured dispersion on flat ends of the
8 scans (second differences, var / mean) is **0.4–1.2** — not the 5 that
t = 0.2 s implies — so each point carries ~5–12× more detected events than
dwell × scans (a multichannel detector sum or intensity correction would do
that; the files do not say which). Consequences:

* Weights ∝ 1/√y have the right SHAPE for a rate; a constant factor does not
  change the fit or the F test (both invariant to it).
* Everything that reads σ in ABSOLUTE terms is calibrated only by the
  coincidence that t_eff ≈ 1 in these units: χ²ᵣ shown to students, the
  detection and proposal SNR gates, the variance floor. Those are exactly the
  sites that break under a unit change. A rescale (kcps, a normalisation, a
  different export) is indistinguishable, to the app, from a noise change.

Options (owner): estimate the noise scale from the data itself (a dispersion
index), which makes every σ-based gate scale-invariant and calibrated; read
dwell × scans from the VGD (the measured dispersion says that alone is off by
5–12×); or keep the counting assumption and document it.

## 3. Scan_6

Correction to the previous report: **no MG2 refit had an unsupported
component** — every slot is supported in every refit (F 128 – 13 000). MG2's
persistence 0.67 is 2 converged of 3 attempted: one refit hit the 18 000-
evaluation cap (χ² 374, as good as the converged 336–379) and counts as absent
for every slot, and the 25 s budget stopped after the third refit. With all 4
refits persistence is 0.75 and MG2 (χ²ᵣ 2.04) wins over AG2 (3.69) — on both
engines. So the move is timing, not this unit; it is not intended by anything.
The design question stands in a different form: one capped or
wall-clock-truncated refit disqualifies the whole model (pre-existing, main).
