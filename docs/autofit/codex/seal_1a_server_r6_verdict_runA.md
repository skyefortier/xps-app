**One MAJOR remains: a non-finite starting value can let a forged request/response pairing read `consistent`.** No honest-response mismatch was reproduced.

Reviewed HEAD `6f09e1d`; checkout unchanged. Validation used source/AST comparisons, committed measurements, **114 verifier cases and 23 server cases invoked directly**, plus in-memory route probes. Session loading was substituted; pytest was not run.

1. **MAJOR — Infinity in a free starting amplitude bypasses request admissibility checks.**

   Reproduction using `_well_posed()` and the existing test helpers:

   ```python
   x, y, specs = SS._well_posed()
   R, O = _seal(
       client, x, y, [{**specs[0], "shape": "gaussian"}],
       background={"method": "none"},
       fit_method="leastsq", seed=12345,
   )
   R["request"]["peaks"][0]["amplitude"] = float("inf")
   _verify(client, R, O)
   # state: consistent, check: None
   ```

   O remains the original, entirely finite response. Posting the changed request to `/api/fit` returns **HTTP 422**. Reproduced for `leastsq`, `nelder`, `differential_evolution`, and `basinhopping`. It also reproduces with the JSON number **`1e400`**, which the parser reads as Infinity; the nonstandard `Infinity` token is unnecessary.

   The new guard recognizes only NaN at [fitting.py:3248](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3248) and [fitting.py:3346](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3346). With a caller seed, verification checks that seed directly at [fitting.py:3383](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3383). It subsequently replaces the infinite free starting value with O’s finite value at [fitting.py:3453](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3453), so subsequent evaluations pass.

   This is a request-admissibility gap: the changed request cannot produce that response through the named fit route. Conservative `unconfirmed/non_finite` handling should cover this surviving non-finite start before it is overwritten. Ordinary infinite bounds need their existing open-bound interpretation preserved.

Both round-5 dispositions pass:

| Disposition | Verification |
|---|---|
| NaN request bounds | Both real-route regression cases return `unconfirmed/non_finite`. |
| Decoder recursion | The deeply nested body returns 400 through [app.py:1389](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1389). |

Across **43 additional Infinity probes**, accepted finite responses verified consistently; non-finite recorded outputs were unconfirmed; invalid manual anchors were refused. The converse forged-pairing case above remains uncovered.

Against the original seven questions:

1. **Pure refactor:** AST comparison confirms the extracted statements retain their operations and order: normalizer **8/8**, background **16/16**, model **5/5**; the app normalizer is the original suffix. Measurements reproduce **187/202 identical**, control differences on **10/15**, and final **8/15 identical plus seven within rounding**. The README appropriately limits the inference.

2. **Statistics:** Association, NumPy reduction, denominators, floor ordering, AIC/BIC, RMSE and null R-factor match the contract. Internal decisions retain lmfit statistics. The summarizer confirms zero measured changes in the four compared statistics across **404 fits**.

3. **Verification:** Exact schema, ownership, roles, held/expression values, seeds, background, curves, areas, associations, statistics and linked-root support are enforced. Whole-software comparison remains conservative. The Infinity-start finding prevents approval.

4. **Option (b):** Consistency remains distinct from acceptance. The unrecomputed fields match the memo: success, message, uncertainties, certificate, starts and required.

5. **Provenance:** Environment and rendered-page/reference hash checks passed. In-memory reload, caching, multiple-template and direct-loader checks preserved each compiled template’s digest. Git status includes ordinary untracked files and respects ignored uploads/environments.

6. **Tests:** All 114 verifier cases passed directly, including both new regressions. Missing coverage is a finite O paired with a non-finite free start. `suites.md` still names **`a71661e`**, not the announced `c0ee89e` full run.

7. **Design rules:** No verification tolerance was introduced. The remaining gap lets fitting consume an infinite start while verification replaces it before judging numerical evaluability.

**VERDICT: NO-GO.**
