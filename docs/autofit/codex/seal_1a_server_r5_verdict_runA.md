**One MAJOR finding remains: an unchanged server response can still read `mismatch`.** No false `consistent` or remaining HTTP 500 was reproduced.

Reviewed `c0ee89e`. Checkout unchanged. Validation used source/AST comparisons, committed measurements, and in-memory route probes with session loading substituted. I did not run pytest.

1. **MAJOR — differential evolution’s accepted NaN bounds falsely invalidate its own response.**

   Reproduction using `_well_posed()`:

   ```python
   x, y, specs = SS._well_posed()
   specs = [{**specs[0], "shape": "gaussian",
             "amplitude_min": float("nan")}]
   R, O = _seal(client, x, y, specs,
                background={"method": "none"},
                fit_method="differential_evolution")
   _verify(client, R, O)
   ```

   `/api/fit` returns **HTTP 200**, with an entirely finite O, nullable bounds, and `success: false`. Verification of that **unchanged response** returns:

   ```text
   mismatch / roles
   p1_amplitude: the recorded value lies outside the request's bounds
   ```

   Independently reproduced with `amplitude_max: NaN`.

   The producer treats any non-finite bound as an open search side at [fitting.py:1781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1781). When refinement fails, it retains the searched response at [fitting.py:1839](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1839). The verifier correctly matches the nullable recorded bounds, but then compares the value against **NaN**, making the range condition false at [fitting.py:3423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3423). Its non-finite scan checks only O at [fitting.py:3274](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3274).

   **Scope:** NaN is nonstandard JSON syntax, but Flask currently accepts it and the producer returns this response. This does not demonstrate failure for ordinary finite browser requests. Nevertheless, under the supplied rubric, an honest O is being rejected; `success: false` is a separate recorded acceptance statement.

   A non-finite effective request bound should receive conservative `unconfirmed` treatment, or be refused consistently by the shared request reader with that behavior change documented.

The round-4 dispositions all pass:

| Disposition | Result |
|---|---|
| Integer lower/upper bounds | Both named regression cases passed. |
| Unevaluable parameters | Lorentzian, DS and pseudo-Voigt overflow cases return `mismatch`. |
| Generic verifier exception | Injected support failure returns `unconfirmed/error`. |
| Overflowing inline arrays | Both energies and counts return HTTP 400. |

Against the original seven questions:

1. **Pure refactor:** AST comparison confirms **8/8**, **16/16**, and **5/5** extracted statements retain their original operations and relative order; the app normalizer is the exact original suffix. The separately documented fixes remain identifiable. Measurements reproduce **187/202 identical**, control differences on **10/15**, and final **8/15 identical plus seven within rounding**. The README appropriately limits these claims.

2. **Statistics:** Association, NumPy reduction, denominators, floor ordering, AIC/BIC, RMSE and null R-factor match the contract. Internal decisions retain lmfit statistics. The summarizer confirms zero measured change in the four compared statistics across **404 fits**.

3. **Verification:** Ownership, schema, seeds, roles, expressions, determinacy, background, arrays, areas, statistics and linked-root support are present. **Sixty additional ordinary fits verified consistently; all 44 existing tamper cases passed.** The finding above remains.

4. **Option (b):** Acceptance remains explicitly recorded rather than proven. The excluded fields match the memo.

5. **Provenance:** Environment hash, rendered-page/reference hashes, and in-memory template reload/interleaving checks passed. Git status includes ordinary untracked files while respecting ignored uploads and environments.

6. **Tests:** Round-4 regressions exercise their named failures. Missing coverage is an accepted NaN request bound producing a finite DE response. At inspection, `suites.md` still recorded the earlier `a71661e` full suite; the supplied 137-pass result was not independently rerun.

7. **Design rules:** No verification tolerance was introduced. The remaining finding gives one bound two interpretations: open during DE search, impossible during verification.

The generic `unconfirmed/error` fallback cannot mark a record current. I found no material false acceptance hidden by it; the remaining defect raises an explicit mismatch and never reaches that fallback.

**VERDICT: NO-GO.**
