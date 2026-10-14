**NO-GO. I reproduced an honest-response rejection and two remaining HTTP 500 paths.** No false `consistent` result was reproduced in this round.

Reviewed implementation `5a6da06`; HEAD `fd785b1` adds only the round-4 prompt. The checkout remains unchanged. Validation used source/AST comparisons, the measurement summarizer, and bounded in-memory probes through the actual routes, substituting session-array loading. I did not run pytest.

1. **MAJOR — free parameters at integer bounds still have two numerical readings.**

   Reproduction using `_well_posed()`’s first peak, Gaussian shape, counts multiplied by `1e10`, background `none`, `n_perturb=0`, and:

   ```json
   {
     "amplitude": 10000000000000001,
     "amplitude_min": 10000000000000001,
     "fix_center": true,
     "fix_fwhm": true
   }
   ```

   `/api/fit` returned HTTP 200 and `success: true`. Its free amplitude and recorded minimum were both `10000000000000000`. Verification of that **unchanged response** returned:

   ```text
   mismatch / roles:
   p1_amplitude: the recorded value lies outside the request's bounds
   ```

   Reproduced with both `leastsq` and `nelder`.

   The producer emits `float(par.value)` and `float(par.min)` at [fitting.py:2883](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2883). Verification compares the recorded bound against its float representation, but then compares the free value against the **original integer bound** at [fitting.py:3418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3418).

   The held-value repair is effective; the free-value bounds check needs the same effective numerical interpretation.

2. **MAJOR — a finite, representable recorded parameter can still crash verification.**

   Produce an honest single-Lorentzian response with `fwhm_max: null`, background `none`, and `leastsq`. It verifies `consistent`. Change only:

   ```text
   individual_peaks[0].params.fwhm.value = 1e200
   ```

   Verification returns HTTP **500**, `"Internal verification error — see server log."`

   `_exact_float` accepts this representable float, and the unbounded role permits it. Evaluation then raises `OverflowError` when computing `hwhm ** 2` at [fitting.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:124). The unguarded evaluation is at [fitting.py:3461](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3461), escaping to the route’s 500 fallback at [app.py:1414](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1414).

   Safe conversion alone does not cover arithmetic failure when evaluating O’s parameters.

3. **MAJOR — overflowing inline request numbers bypass validation and return HTTP 500.**

   Independently replacing either `R.energies[0]` or `R.counts[0]` with `10**400` returned HTTP **500**, `"Internal server error"`.

   Both arrays are converted with `np.asarray(..., dtype=float)` at [app.py:1397](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1397), but the handler catches only `TypeError` and `ValueError` at [app.py:1402](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1402). `OverflowError` escapes before the verifier runs. This should receive a controlled invalid-request response.

The five round-3 dispositions:

| Disposition | Result |
|---|---|
| Held integer | Regression passed: honest float consistent; unequal integer rejected. Free-bound counterpart remains finding 1. |
| ID schema | Boolean, null, text, integer and `10**400` ID probes passed. |
| Overflowing O integers | All six new regression cases passed. Findings 2–3 expose additional exception paths. |
| LA ordering | Regression passed: the later stable component’s mismatch wins over earlier LA uncertainty. |
| Meaningful huge-integer tests | All nine integer-neighbor cases passed. They now exercise unequal integers sharing the honest float. |

Against the original seven questions:

1. **Pure refactor:** AST comparison confirms the extracted statements and relative order: normalizer **8/8**, background **16/16**, model **5/5**; the app normalizer is the exact original suffix. Previously disclosed fixes remain separate. Measurements reproduce **187/202 identical**, control differences **10/15**, and final **8/15 identical plus seven within the existing comparator**. These are sampled evidence; the README’s residual-vector overclaim remains removed.

2. **Statistics:** Association, NumPy reduction, denominators, reduced-chi-square-before-floor order, AIC/BIC, RMSE and null R-factor match V6.6. Internal decisions retain lmfit’s statistics, including required-refit `chi2_with`. The summarizer confirms zero measured differences in the four compared statistics across **404 fits**.

3. **Verification:** Ownership, schema, starting-parameter seeds, roles, held/expression values, determinacy, background/verdict, curves, areas, array associations, statistics and linked-root support are implemented. Whole-software comparison remains conservative and appropriate. Findings 1–3 prevent approval.

4. **Option (b):** The consistency-versus-acceptance wording remains honest. Unrecomputed fields match the memo: success, message, uncertainties, certificate, starts and required.

5. **Provenance:** No additional defect found. Environment hashing uses the stated sorted distribution list. Git status includes ordinary untracked files; uploads, environments and `.claude/` remain ignored. Template digests belong to compiled template objects; reference hashing uses the injected object.

6. **Tests:** The round-3 regressions passed when invoked with in-memory session loading. Missing coverage is demonstrated by the three findings above. The supplied 137-pass result was not independently rerun; `suites.md` still records the earlier `a71661e` full-suite result.

7. **Design rules:** No verification tolerance was introduced. Finding 1 remains a concrete violation of “Two readings of one field.”

**VERDICT: NO-GO.**
