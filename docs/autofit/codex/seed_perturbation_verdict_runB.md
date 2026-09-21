Reviewed implementation commit `aca6e64`. Actual HEAD, `a530a83`, only adds the review prompt. No files changed.

1. **MAJOR — `/api/analyze` can bypass seeding.** [fitting.py:1340](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1340)

   The exact-string check covers only two spellings, but `/api/analyze` forwards `options.fit_method` without `/api/fit`’s allowlist.

   **Reproduced:** an otherwise valid manual-model analyze request with `"fit_method": "BasinHopping"` returns HTTP 200. lmfit normalizes the name, invokes basinhopping with `seed=None`, and consumes NumPy’s global RNG. Replaying the identical request after global seeds `0` and `12345` produced different fitted parameters. `"fit_method": "ampgo"` also returns HTTP 200 and consumes the global RNG.

   Normalize and validate methods at the shared boundary, then seed every accepted stochastic method—or reject unsupported ones. This breaks the claimed coverage of every random draw reachable through these APIs.

2. **MINOR — Cosmetic fields and equivalent background representations change the random experiment.** [fitting.py:1131](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1131)

   Entire peak dictionaries and unsorted manual anchors enter the hash.

   **Reproduced through `/api/fit`, using page-style fields and upload-rounded data:** changing only the first peak’s name from `C-C` to `Graphite` changed:
   
   | | `C-C` | `Graphite` |
   |---|---:|---:|
   | Seed | 2364941963 | 827839811 |
   | Reduced χ² | 1.69345 | 1.45970 |
   | First component area fraction | 50.36% | 42.51% |

   Likewise, placing identical manual anchors in reverse order produces different seeds, although both background implementations sort them before interpolation. Consider hashing normalized numerical inputs, excluding display names. This affects equivalent-model reproducibility; it does not violate literal identical-request replay.

**a. Canonicalisation and upload stability.** The two page-reachable examples above are concrete. Numeric versus string peak IDs, signed zero, and absent versus null also hash differently in direct calls, but the page always stringifies IDs and JSON serialization collapses numeric `-0` to `0`. Background indices are coerced by `/api/fit`; integer versus float spelling hashes identically. Nonfinite uploaded rows are removed by the parser; browser JSON serializes NaN as null.

Different numerical requests can share a seed: using `_two_peaks()`, linear background, `leastsq`, three perturbations, and otherwise identical defaults, first-peak centers **284.62693** and **284.74390** both produce **2593011075**. That is an ordinary 32-bit collision, not a broken hash implementation.

The CSV→parser→NPZ path is stable for repeated identical input. I verified repeated parsing and NPZ serialization/loading in memory. UUIDs and archive metadata do not enter the seed.

**b. Stream separation.** `SeedSequence.spawn(2)` is used correctly. Solver-seed consumption cannot advance the perturbation stream. Each stochastic minimisation receives a new seed; DE refinement and the competing local fit receive none. Duplicate solver seeds remain theoretically possible because sampling is with replacement, but are negligible at this trial count. Changing the method changes the request hash and therefore both streams—intentional, rather than accidental coupling.

**c. Caller seeds.** Replacing the request-derived seed is reasonable as an explicit override. Nonnegative integer seeds work for the two covered stochastic methods; negative integers raise `ValueError`. Boolean, float, and string seeds are silently ignored and replaced with the derived seed.

There is an existing interface limitation: `{"method":"leastsq","fit_kws":{"seed":4}}` still forwards `seed` into the deterministic solver and raises `RuntimeError`. The claimed request-wide override is therefore not usable uniformly across methods.

**d. Distribution and autofit.** I found no systematic preference for worse minima caused by SHA-256 or the stream split. A fixed request can permanently receive an unlucky draw; that is inherent in the requested policy. Different requests generally receive different streams.

`autofit/engine.py` and `bayesian_exchange_mc.py` use their explicit local generators; I found no additional global RNG dependency there. Autofit’s manual-model wrapper now inherits seeded perturbations when requested. Its default deterministic fit with zero perturbations has unchanged solver behaviour.

**e. Trust-Region analysis.** The explanation is technically credible: I independently reproduced three dot-product results for identical 13-element vectors at different alignments, while `np.sum(w*w)` remained constant. The installed TRF implementation uses `numpy.linalg.norm` and dot products. I did not independently repeat the claimed first-divergence trace or 202-target measurements.

Avoiding a SciPy-internals patch is appropriate. A controlled numerical stack using a reproducibility-capable BLAS is a sound investigation; for example, [oneMKL CNR](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2024-1/conditional-numerical-reproducibility-control.html) supports reproducible arithmetic under specified conditions. That requires end-to-end validation, not merely setting a seed. Also qualify long-term draw compatibility: [NumPy’s compatibility policy](https://numpy.org/doc/2.0/reference/random/compatibility.html) does not promise unrestricted Generator compatibility across versions and environments.

**f. Tests and consumers.** **13 passed; two upload-writing tests were excluded to preserve read-only operation.** Against `main` loaded in memory, the perturbed-start regression test and pinned-seed test both failed as expected.

Missing coverage includes analyze-method bypasses, cosmetic normalization, caller-seed types, cross-process replay, and saved-project replay. The Trust-Region “identical factors” test actually compares starting parameters approximately; it never captures or asserts exact random factors. The stochastic tests verify supplied seeds, not global-state independence or returned results.

No consumer break from `random_seed` was found. However, saved projects omit `backendResult` and its seed. Also, successful fits overwrite starting parameters, so another button press—or refitting a saved result—sends a different request. This change alone does not guarantee those workflows regenerate the original answer.

**VERDICT: NO-GO.**
