**NO-GO. I reproduced an honest-response rejection and a remaining HTTP 500 path driven by a finite value in O.** No false `consistent` result was reproduced.

Reviewed implementation `5a6da06`; HEAD adds only the round-4 prompt. The checkout remains unchanged. Validation used source/AST comparisons, the measurement summarizer, and bounded in-memory probes through the actual routes, with session loading supplied from memory. I did not run pytest.

1. **MAJOR — free parameters at integer bounds can still make honest responses stale.**

   The producer records parameter values and bounds as floats. Verification compares the recorded bounds with floats, but then checks the free value against the original, potentially integer bounds.

   Reproduction: use `_well_posed()`’s first peak as Gaussian, background `none`, `n_perturb=0`, hold center and FWHM, and set:

   ```json
   {
     "amplitude": 10000000000000001,
     "amplitude_min": 10000000000000001
   }
   ```

   `/api/fit` returns **HTTP 200, `success: true`**, with amplitude value and minimum both `1e16`. Its unchanged response verifies as:

   ```text
   mismatch / roles
   p1_amplitude: the recorded value lies outside the request's bounds
   ```

   Reproduced with both `leastsq` and `nelder`. The upper-bound counterpart also fails: `amplitude_max = 10000000000000003` produces value/max `10000000000000004`, then `mismatch/roles`.

   Evidence: producer conversions at [fitting.py:2883](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2883); float-bound comparison at [fitting.py:3411](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3411); original-bound comparison at [fitting.py:3418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3418).

   The held-value fix works, but the bounds still have two numerical readings.

2. **MAJOR — representable finite O values can overflow during evaluation and return HTTP 500.**

   Produce an honest Lorentzian response with `fwhm_max: null`. It returns `success: true` and verifies `consistent`. Change only:

   ```text
   individual_peaks[0].params.fwhm.value = 1e308
   ```

   Verification returns **HTTP 500**, `"Internal verification error — see server log."`

   `_exact_float` accepts this finite, representable value, and it lies within the request’s open bound. Component evaluation then raises `OverflowError` while squaring the half-width. The exception escapes the verdict handling. The same failure reproduces for Doniach–Šunjić and pseudo-Voigt.

   Evidence: unchecked evaluation at [fitting.py:3461](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3461), overflowing arithmetic at [fitting.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:124) and [fitting.py:207](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:207), HTTP fallback at [app.py:1414](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1414).

   Conversion safety does not yet ensure that a recorded parameter receives a verification verdict.

3. **MINOR — overflowing inline request data bypass the malformed-body refusal.**

   Independently replacing `R.energies[0]` or `R.counts[0]` with `10**400` returns **HTTP 500**, `"Internal server error"`.

   The array conversion catches `TypeError` and `ValueError`, but omits `OverflowError`: [app.py:1397](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1397), [app.py:1402](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1402). This malformed-R case should receive the existing 400 response. It does not establish false consistency or false STALE.

The five round-3 dispositions:

| Disposition | Assessment |
|---|---|
| Held integer | Named regression passes: honest float accepted, unequal integer rejected. Finding 1 remains for **free values at bounds**. |
| ID schema | Boolean, null, text and integer cases pass; the scalar schema addresses the reported rejection. |
| Integer overflow in O | All six regression cases pass, including recorded stderr. Finding 2 exposes a later arithmetic overflow. |
| LA ordering | Regression passes; stable component failures are checked before deferred LA uncertainty. |
| Same-float integers | All nine cases pass. These now exercise unequal integers that share the honest float, unlike the previous test. |

Against the seven original questions:

1. **Pure refactor:** AST/source comparison confirms the extracted normalizer, background and model statements preserve their original operations and relative order; the app normalizer is the original suffix. The separately documented wording, ownership and signed-zero fixes remain identifiable. Measurements reproduce **187/202 identical**, control differences on **10/15**, and final **8/15 identical plus seven passing the existing comparator**. These are sampled evidence, not universal identity.

2. **Statistics:** `_fit_statistics` matches the required association, NumPy reduction, denominators, reduced-chi-square-before-floor ordering, AIC/BIC, RMSE and null R-factor. Internal decisions retain lmfit statistics, including required-refit `chi2_with`. The summarizer confirms **zero measured change in all four compared statistics across 404 fits**.

3. **Verification:** Schema, ownership, starting-parameter seed derivation, expressions, determinacy, complete background assembly, array relations, areas, statistics and linked-root support are present. Whole-software comparison and non-finite handling remain conservative. Findings 1–2 prevent a clean pass.

4. **Option (b):** The consistency-versus-acceptance distinction remains honest. The unrecomputed fields match the memo: success, message, uncertainties, certificate, starts and required. No convergence or minimum proof is claimed by `consistent`.

5. **Provenance:** Environment hashing matches the sorted installed-distribution contract. Git status includes ordinary untracked files while ignored uploads/environments remain excluded. An in-memory reload/interleaving probe confirms each compiled template retains its own digest, including multiple template names. Reference hashing uses the injected object.

6. **Tests:** The round-3 regressions now test their named defects meaningfully; the all-lineshapes helper permits LA’s intended uncertainty. Missing cases are free parameters landing on rounded integer bounds, representable values overflowing evaluators, and overflowing inline R arrays. The supplied 137-pass result does not cover these. `suites.md` still records the earlier `a71661e` full suite.

7. **Design rules:** No verification tolerance was introduced. Finding 1 still violates “Two readings of one field.”

**VERDICT: NO-GO.**
