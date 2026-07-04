**Math Checks**
- `-(n/2) log RSS` is correct for Gaussian iid noise with unknown scale and Jeffreys prior `p(sigma) ∝ 1/sigma`, up to constants independent of `theta`. For same data/window and one shared noise scale per candidate, those constants cancel in model comparison.
- The stepping-stone identity is valid for `p_beta(theta) ∝ RSS(theta)^(-beta*n/2)` over a proper bounded prior.
- The `beta=0` replica is the normalized uniform prior in effect: the estimator computes `Z(1)/Z(0) = (1/V) ∫ L(theta)dtheta`, so differing prior volumes/parameter counts are not omitted. They affect `ΔF` correctly through the `Z0` normalization.
- Exchange sign at [bayesian_exchange_mc.py:193](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:193) is correct.
- Burn-in-only adaptation is compatible with detailed balance only after freeze; the post-burn kernel is fixed. The claim is acceptable if scoped to post-burn.
- Per-coordinate Metropolis with out-of-bounds reject at [bayesian_exchange_mc.py:171](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:171) preserves the bounded-uniform-prior target.

**Findings**
1. **BLOCKER**: `free_energy` is used as if exact, with no Monte Carlo error bar.
   Lines: [bayesian_exchange_mc.py:205](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:205), [bayesian_exchange_mc.py:347](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:347), [test_bayesian_method.py:58](/Users/skyefortier/xps-app/tests/autofit/test_bayesian_method.py:58)
   Failure scenario: tests use only ~250 post-burn samples/rung; defaults only 750. Correlated rung draws make the log-mean stepping-stone estimator biased and noisy, but posterior weights are reported as decisive. A near-tie or seed-sensitive real model can flip.
   Fix: compute/report `free_energy_se` and per-rung ESS, preferably via batch means or independent seeded runs; suppress decisive posterior weights when `ΔF` is not large relative to MC error.

2. **BLOCKER**: CI payload remains too strong under low ESS.
   Lines: [bayesian_exchange_mc.py:321](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:321), [bayesian_exchange_mc.py:333](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:333), [bayesian_exchange_mc.py:438](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:438)
   Failure scenario: warning is only buried in candidate analysis; `confidence[*].sigma_stat` still advertises `posterior_ci` values. Downstream users can consume narrow CIs without seeing that they are low-ESS random-walk quantiles.
   Fix: propagate reliability into each `sigma_stat`; downgrade kind/status when ESS is low, or withhold intervals unless ESS and chain diagnostics pass.

3. **MAJOR**: stuck chains can get falsely high ESS.
   Lines: [bayesian_exchange_mc.py:248](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:248), [bayesian_exchange_mc.py:250](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:250)
   Failure scenario: a free parameter that never moves has zero variance, returns `ESS = n`, and can produce a zero-width “credible interval” with no warning.
   Fix: treat zero variance for a free sampled parameter as `ESS=0` or emit `stuck_chain_warning`, unless the parameter is truly fixed and excluded from sampling.

4. **MAJOR**: current tests can pass with wrong evidence math.
   Lines: [test_bayesian_method.py:68](/Users/skyefortier/xps-app/tests/autofit/test_bayesian_method.py:68), [test_bayesian_method.py:74](/Users/skyefortier/xps-app/tests/autofit/test_bayesian_method.py:74)
   Failure scenario: strong synthetic peak-count recovery would still pass if likelihood constants, prior normalization, or stepping-stone bias were wrong enough to matter only in close models.
   Fix: add an analytic evidence test. Best target: 1D Gaussian mean model with uniform prior and Jeffreys-marginalized sigma, where `RSS(mu)=S+n(mu-ybar)^2` and evidence is known by Student-t CDF or high-precision quadrature. Include two prior widths to verify the prior-volume Occam factor.

5. **MINOR**: `free_energy` is relative, not absolute.
   Lines: [bayesian_exchange_mc.py:113](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:113), [bayesian_exchange_mc.py:224](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:224)
   Failure scenario: later code may compare `F` across different datasets/windows and assume absolute log evidence.
   Fix: document that omitted likelihood constants cancel only for same-data candidate comparisons; store `free_energy_is_relative=True` or equivalent.

VERDICT: NO-GO (blockers: free-energy uncertainty is unreported; posterior_ci remains overclaimed under low/stuck ESS)
