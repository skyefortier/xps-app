# Codex verdict trail — empirical noise estimator (autofit/noise.py), 2026-07-04/05

Every round ran TWICE (severity-nondeterminism rail; stricter verdict
governs). Prompts committed alongside
(`noise_model_math_review_prompt.txt`, `noise_model_recheck_prompt.txt`,
`noise_model_recheck2_prompt.txt`, `noise_model_recheck3_prompt.txt`).
Full dispositions live in the PROGRESS.md noise sections; this file is the
verdict record.

## Round 1 — dedicated math review: NO-GO ×2
Blockers/majors (both runs converged): scalar variance corrections are
not exact after the data-adaptive residual stack (regression leverage,
registration selection-on-noise, filter edges — measured b centering
≈0.92 under modest shifts); edge_drop=3 insufficient for the survey's
~0.3 eV shifts; survey prose overreach (sub-Poisson claim from
drift-dominated rows); tests non-discriminating; stale docstring.
→ FIXED: explicit operator T with exact per-point transmission;
residual-shift-coefficient sign selection; Newton shift refinement;
dynamic edge masks; Monte Carlo pins; survey reworded.

## Round 2 — re-check: NO-GO ×2
Two NEW real blockers: (1) interpolation COVARIANCE — linear registration
correlates adjacent aligned samples (f(1−f)σ²), which no diagonal factor
carries; (2) DESCENDING BE grids — real raw_be grids descend and np.interp
silently returns garbage, invalidating ALL prior real-data registration
(including the then-current "sub-Poisson b=0.61–0.92" survey narrative).
Majors: mask-cap silent under-masking; per-scan intensity assignment
question; survey prose (Cl2p mislabeled clean; a 1.008 eV shift row
contradicting the quoted range).
→ FIXED: transmission through the explicit interpolation matrix
(u,w = (T²+(TP)²)·{1, I}); internal grid reversal (asc/desc equivalence
pinned 1e-9); refusal flags; per-scan intensity assignment TRIED and
measured catastrophically wrong (regressor shares response noise —
b→0.38 pure Poisson) → ensemble-mean kept with an
intensity_assignment_degraded flag (measured ~18% understatement at
6-step shifts, documented lower bound); survey regenerated under VALID
registration — the three flag-clean groups give b = 0.95–1.38
(near-Poisson, tentative); the sub-Poisson reading RETRACTED.

## Round 3 — re-check: NO-GO ×2
Blocker: the covariance pin rebuilt the operators inside the test — a
production regression to diagonal-only would still pass. Majors: refusal
paths lose their diagnostics (generic concatenate error / NaN "fit");
stale diagonal-factor prose.
→ FIXED: operators factored to module-level production helpers used by
both the estimator and the pin; three-layer pin (deterministic identity
vs independent dense diag(TΣTᵀ) at 1e-10; NEGATIVE CONTROL proving the
diagonal-only predictor fails; MC sanity); total-sample-count guard
raising with pair_excluded reasons (reachable-path test);
no_diagnostic_bins flag; prose scrubbed.

## Round 4 — re-check: **GO ×2**
All dispositions verified closed. The empirical noise estimator unit is
review-complete: replicate-difference σ²(I)=a+b·I with covariance-exact
transmission, registration, honest refusal/degradation flags, ground-truth
+ Monte Carlo + production-path pins, and a real-data survey that says
exactly what it can and cannot support.
