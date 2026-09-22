1. **MAJOR — DE silently bypasses the check.** `fitting.py:1375` calls `model_without.fit()` directly, bypassing DE’s finite-bound and refinement machinery. Reproduced on the redundant-anchor fixture with `differential_evolution`: the full fit succeeds, but `required` returns `{ran:false, reason:"error"}` because amplitudes have infinite upper bounds. The page consequently accepts the unchecked anchor. Use the existing DE candidate machinery for the reduced model.

2. **MAJOR — The request can check the wrong component after a tab switch.** `templates/index.html:7262` reads `state.peaks` **after** awaiting upload, whereas `peakSpecs` was captured before it. Reproduced a request containing tab A’s Graphite id `11`, but `require_component:"12"` from tab B. If id `12` exists in A and the user returns to A before completion, another component’s verdict can authorize A’s redundant Graphite anchor. Capture the anchor id alongside `peakSpecs`.

3. **MAJOR — Transitive links break the reduced model.** `fitting.py:1740` drops only direct dependents; `fitting.py:1371` likewise filters only expressions mentioning the original anchor. Reproduced a valid `1 → 9 → 10` dependency chain: the full fit succeeds, but removing `1` yields `NameError: name 'p9_amplitude' is not defined`, producing a nonblocking error verdict. Remove the complete dependency closure and its parameters.

4. **MINOR — Stochastic refits lose request seeding.** `fitting.py:1749` passes raw `kws`, bypassing `seeded()`. Instrumentation recorded basinhopping calls with seeds `4110636191` for the full fit and `None` for the refit. Identical requests therefore use uncontrolled random draws for the required-component decision. Pass a request-derived solver seed.

5. **MINOR — Corpus regression coverage is machine-dependent.** `tests/test_component_required.py:83` references an absolute path in another worktree and silently skips elsewhere. Even when present, line 89 checks only 10 of 70 models. A clean CI checkout cannot enforce the claimed corpus protection.

Four selected Python tests and all three new JavaScript tests passed. An exact duplicate-peak construction correctly returned “not required.” Starting from fitted values is a valid redundancy comparison; permitted movement onto the anchor demonstrates redundancy under those bounds. One local refit can still miss a better basin, and `n_perturb` is not rerun.

The F definitions match the requested rule. Gate ordering, rollback, and ordinary Run Fit’s `required:null` path look correct. Accepted metadata stays in `backendResult`; the explicit save serializers do not add a `required` field.

**VERDICT: NO-GO.**
