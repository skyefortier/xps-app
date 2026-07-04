1. **BLOCKER** [bayesian_real_validation_runs.jsonl](/Users/skyefortier/xps-app/docs/autofit/inventory/bayesian_real_validation_runs.jsonl:29), [test_bayesian_real_gate.py](/Users/skyefortier/xps-app/tests/autofit/test_bayesian_real_gate.py:41), [run_bayesian_real_validation.py](/Users/skyefortier/xps-app/scripts/run_bayesian_real_validation.py:179)  
   The U 4f seed-flip validation is not actually closed. The artifact still records seed 0 as U1b `F=2803.153` vs U2 `2806.311`, and seed 1 as U2 `2800.134` vs U1b `2806.578`, but it has no `free_energy_split_half_error`, no `posterior_weight_reliable`, no `model_selection_warning`, and old confidence payloads without per-slot reliability/ESS. The real gate only exercises Cl 2p, so the exact motivating U 4f flip can still regress without CI noticing.  
   Failure scenario: a consumer of the validation artifact still sees decisive posterior weights `0.959` and `0.998` on the flipped U 4f winners, with no unresolved-selection warning.  
   Fix: rerun/regenerate the JSONL with the fixed method, persist `analysis.model_selection_warning`/`free_energy_is_relative` or full diagnostics, update the summary to show split-half errors/reliability, and add an env-gated U 4f test asserting the top-2 comparison is `UNRESOLVED` and top candidate weights are unreliable for seeds 0/1.

2. **MAJOR** [test_bayesian_method.py](/Users/skyefortier/xps-app/tests/autofit/test_bayesian_method.py:92)  
   The blocker #2 and stuck-chain fixes are present in code but not regression-pinned. The test checks `uncertainty_kind` and candidate-level `ci_reliability_warning`, but never asserts `sigma_stat.reliability`, `reliability_note`, per-interval `ess`, or zero-variance ESS returning `0`.  
   Failure scenario: a later refactor can remove the consumer-visible reliability fields from `_posterior_peaks`, or revert zero-variance ESS to `n`, while these tests still pass.  
   Fix: assert the new `sigma_stat` contract and add a direct zero-variance ESS/stuck-chain test.

**Disposition Check**

1. F uncertainty: live method closes the code path. Split-half error is computed per run at [bayesian_exchange_mc.py](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:226), copied per candidate at line 347, warning is in analysis/diagnostics at lines 427 and 443, and `posterior_weight_reliable` is set at line 403.

2. CI overclaim: live payload closes it. `_posterior_peaks` adds per-interval `ess` at line 493 and slot-level `reliability`/`reliability_note` at lines 517-518.

3. Stuck chains: live ESS code closes it. Zero variance now appends `0.0` at [bayesian_exchange_mc.py](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:268).

4. Analytic evidence test: reference math is right. It computes `(1/V) ∫ RSS(mu)^(-n/2) dmu` after factoring out `S^(-n/2)`, matching the sigma-marginalized likelihood scale. The width 4 vs 16 check should produce `log(4)` because both windows contain essentially all mass. `abs=0.3` on estimator-vs-quadrature is meaningful, not vacuous, relative to `log(4)=1.386`.

5. Relative F: closed in live analysis at [bayesian_exchange_mc.py](/Users/skyefortier/xps-app/autofit/methods/bayesian_exchange_mc.py:431), with the docstring note at lines 34-39.

I could not run pytest in this read-only sandbox; Python/pytest failed because no writable temporary directory is available for capture files.

VERDICT: NO-GO (blockers: real-data U 4f unresolved-warning validation artifact/gate is stale/missing)
