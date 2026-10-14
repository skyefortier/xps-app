# Seal 1a′ — measurements (2026-10-13)

Branch `seal-1a-server`; plan `docs/superpowers/plans/2026-10-13-seal-1a-server.md`. Targets: the
202 committed fit targets (`optimizer-disagreement/targets.json`, built by
`scripts/optimizer_disagreement_targets.js`), each fitted with the page's request (full-precision
arrays, the target's background, n_perturb 3). Numbers below: `python scripts/seal_1a_summarise.py`.

## 1. Statistics formed from the returned arrays (V6.6)

`scripts/seal_1a_statistics_measure.py` — ONE fit per target; lmfit's chi-square, reduced
chi-square, AIC and BIC beside the array-formed values of the same fit (so the difference is the
change, not optimiser jitter); also whether lmfit's `best_fit` is the returned `fitted_sub`,
whether `result.nvarys` is the roles count, and the in-process verification's verdict.

| method | targets | statistics identical (each of χ², χ²ᵣ, AIC, BIC) | best_fit = fitted_sub | nvarys = roles | verify consistent |
|---|---|---|---|---|---|
| Trust-Region (`statistics_tr.jsonl`) | 202, all converged | 202 / 202 | 202 / 202 | 202 / 202 | 202 / 202 |
| Levenberg-Marquardt (`statistics_lm.jsonl`) | 202, all converged | 202 / 202 | 202 / 202 | 202 / 202 | 202 / 202 |

Reading: on the committed targets lmfit's last residual evaluation IS the returned model, so the
array-formed statistics are bit-for-bit lmfit's. The change makes them recomputable from the
response; it moves no reported number on these targets. (It can differ where the minimiser's last
evaluation is not at the returned parameters; none of the 404 fits is such a case. The unit
reports no size it did not measure.) Release note: none needed for the numbers; `rmse` and
`fitted_sub` are new fields.

## 2. The refactor is the code it replaced

`scripts/seal_1a_identity.py` — main's `fitting.py` (ef750f6) and the branch's loaded into one
process, each target fitted by both (Levenberg-Marquardt, n_perturb 3), complete responses compared
(`software` excluded: it names the checkout).

- Refactor-only code (`refactor_identity_lm.jsonl`): identical on 187 / 202. The 15 that differ are
  11 U 4f models with LA(α,β,m) (`np.convolve`'s alignment-dependent dot product, CLAUDE.md
  "Reproducibility") and 4 C 1s fits carrying Trust-Region arithmetic (the minimum certificate's
  continuation; BLAS alignment).
- CONTROL, main against an identical copy of main on those 15 (`control_main_vs_main_lm.jsonl`):
  differs on 10 in the same fields; identical on 5 in that run. The jitter depends on where arrays
  land in memory, so one identical control run does not make a target deterministic; the
  within-rounding verdict below is the test.
- FINAL code against main on the 15 (`final_identity_differing_lm.jsonl`), each judged by the
  repo's same-fit standard (`tests/fit_equality.py`): identical on 8 / 15 this run; the other 7
  (3 + 1 C 1s, 3 U 4f) are the SAME FIT within rounding, every one; none differs beyond rounding.
  The only added fields are `fitted_sub` and `statistics.rmse`; nothing removed.

## 3. Verification

Every one of the 404 fits above verifies `consistent` in the process that made it. Cross-process
bit-stability per lineshape (LA's `np.convolve`, DS+G's FFT) is unit 1b's measurement (V6.5, Q7):
the identity run above already shows LA curves can differ between two evaluations of the same
parameters in one process, so an LA fit recorded by one worker may read `mismatch` in another
until 1b decides.
