Reviewed implementation commit `aca6e64` against `main`. Actual HEAD, `a530a83`, only adds the review prompt. No files changed.

1. **MAJOR — Stochastic methods reachable through `/api/analyze` remain unseeded.** [fitting.py:1340](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1340)  
   `/api/analyze` accepts `method: "least_squares"` with `options.fit_method` forwarded without the `/api/fit` allowlist. `ampgo`, `dual_annealing`, and uppercase `BASINHOPPING` bypass seed injection; lmfit recognizes them. Confirmed through Flask with an in-memory session: all returned HTTP 200 and consumed NumPy’s global generator. For one bounded Gaussian with only amplitude varying, identical `ampgo` requests produced amplitudes **1002.972284 versus 1002.948106** after changing global RNG state. Normalize and validate methods centrally; either cover additional stochastic methods or reject them.

2. **MINOR — Cosmetic peak names change the scientific result.** [fitting.py:1131](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1131)  
   The hash includes the whole peak dictionary, including `name`, which fitting otherwise ignores. Using the crowded C 1s fixture with page-style string IDs, fix flags, and rounded data, changing only `Graphite` to `C-C` changed χ²ᵣ **1.459704 → 1.693453** and the third component’s area fraction **18.953% → 5.435%**. This satisfies literal request identity, but fails semantic identity for cosmetic edits. Exclude presentation metadata from seed derivation.

3. **MINOR — The advertised caller-seed override breaks local solvers.** [fitting.py:1341](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1341)  
   `fit_kws={"method":"least_squares","fit_kws":{"seed":4}}` selects master seed 4, then forwards that same keyword to SciPy. Confirmed failure: `least_squares() got an unexpected keyword argument 'seed'`. Consume the master-seed option before forwarding solver kwargs. The page cannot trigger this because its route only forwards the method.

4. **MINOR — The Trust-Region draw test tests solution-dependent starts and fails on the supported local environment.** [tests/test_fit_reproducibility.py:104](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/tests/test_fit_reproducibility.py:104)  
   Despite its comment, it never divides by the first solution or records RNG draws. My run failed on `p3_gl_ratio`: **0.0354818385 versus 0.0355270568**, outside its relative tolerance. Record the actual draws and assert those exactly; keep numerical-result checks separate.

**a. Canonicalisation and uploads.** Besides names, absent `constrain_to` versus `constrain_to: null` produces different seeds for equivalent unconstrained peaks. Integer/string IDs and signed zero also hash differently, but the page’s `String(p.id)` and JSON serialization remove those particular spelling variations. Background indices are converted to integers by Flask. NaN is not an ordinary page input: JSON converts it to null, and uploaded nonfinite rows are filtered.

Different numerical requests can share a seed. I found this concrete 32-bit collision:

- Energy `[1,2,3]`, counts `[10,20,10]`; one Gaussian, ID `"1"`, amplitude `10`, FWHM `1`.
- Background `none`, indices `0,3`, endpoint average `1`, no manual background, method `leastsq`, `n_perturb=3`.
- Center **1.662183** and **1.681107** both yield **3964805149**.

That is acceptable for an RNG seed; it must never become a cache identity. The page’s four-decimal energy/two-decimal intensity CSV conversion is deterministic. Repeated parsing and compressed-NPZ round trips were bit-identical in memory; session UUIDs do not enter the hash.

**b–d. Streams, overrides, and bias.** `SeedSequence.spawn(2)` is used correctly. Solver seeds advance per minimisation; DE refinement/local candidates receive none. Solver consumption does not advance the perturbation generator. Changing the method changes the master hash, so it also changes perturbations—deliberately, given this design.

I found no systematic distribution bias or universal reuse of three scale factors. A fixed request can permanently receive an unlucky draw; that is inherent in the requested policy. Thirty-two-bit collisions are expected, but four solver draws have negligible accidental-repeat probability.

Replacing the request seed entirely is reasonable for an explicit override. Nonnegative Python/NumPy integers work as master seeds; negative integers fail. Bool/float/string values fall back to request hashing and are overwritten for the two recognized stochastic methods, but remain invalid forwarded kwargs for local solvers.

**Other sites and consumers.** `autofit/engine.py` and `bayesian_exchange_mc.py` use explicit local generators; I found no additional global RNG dependency in their sampling paths. Engine fits use `leastsq`. Autofit’s manual baseline now receives deterministic perturbations when requested; its default `n_perturb=0` local fit has no intended numerical change.

No inspected consumer rejects `random_seed`. Frontend consumers select known fields; autofit selects fields into `MethodResult`. Project serialization omits `backendResult`, so the new seed is **not persisted** there. Also, ordinary successive Run Fit presses send updated fitted parameters after `applyBackendResult`; they are not necessarily identical requests.

**e. Trust-Region analysis.** The alignment mechanism is credible and reproducible: my alignment probe produced different dot/norm results for identical vectors. However, this environment reports **Apple Accelerate**, so it does not establish the paragraph’s OpenBLAS attribution. Avoiding a SciPy-internals patch is sound. A controlled numerical backend is another avenue—oneMKL documents conditional reproducibility—but requires whole-pipeline validation, not merely seeding or tighter tolerances. [Intel reproducibility conditions](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2025-0/reproducibility-conditions.html)

The seed hash is portable for identical normalized inputs; indefinite draw compatibility is a stronger claim than `default_rng` guarantees with unpinned dependencies. [NumPy compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html)

**f. Tests.** Local result: **12 passed, 1 failed, 2 upload tests excluded** because disk writes are prohibited. Against `main`, the perturb-start regression and pinned-seed test both failed as expected. Missing coverage includes analyze-method bypasses, caller seeds with local solvers, cosmetic equivalence, fixed expected RNG samples, separate processes, and the actual page’s update-and-resubmit behavior.

**VERDICT: NO-GO.**
