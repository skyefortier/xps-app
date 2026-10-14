**NO-GO.** I reproduced a false `consistent` result and two honest-response failures.

Reviewed implementation `4c2cfde`; HEAD `ec71deb` adds only the round-3 prompt. The checkout is unchanged. I used source/AST comparisons and bounded in-memory probes, including the actual fit and verification routes with session loading supplied from memory. I did not run pytest.

1. **BLOCKER — held parameters and their bounds still have two numerical readings.**

   Using `_well_posed()`, counts scaled by `1e12`, its first peak as Gaussian, background `none`, and `n_perturb=0`, set:

   ```json
   {
     "amplitude": 10000000000000001,
     "amplitude_min": 10000000000000001,
     "fix_amplitude": true
   }
   ```

   `/api/fit` returned HTTP 200, `success: true`. Then:

   | Recorded amplitude value | Verification |
   |---|---|
   | Honest response: `10000000000000000` | `mismatch / held` |
   | Change only that value to integer `10000000000000001` | **`consistent`** |

   Bounds clipping can leave the effective parameter holding the exact integer. The producer serializes `float(par.value)`, whereas verification compares against the unconverted effective value. These are different numbers, not equivalent JSON spellings.

   Evidence: producer conversion at [fitting.py:2883](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2883); held comparison at [fitting.py:3400](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3400); final parameter comparison at [fitting.py:3418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3418).

   Effective parameters and their recorded representation need one shared numerical reading.

2. **MAJOR — the new ID schema rejects responses the producer accepts.**

   With the Gaussian fixture, requests containing `id: true` or `id: null` each returned HTTP 200 and `success: true`. Their unchanged responses both verified as:

   ```text
   mismatch / schema: certificate is not of a response's form
   ```

   Request validation permits these IDs, and `_certificate_report` copies them verbatim. `_ID_T` permits only strings and non-boolean integers.

   Evidence: request validation at [app.py:104](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:104); producer at [fitting.py:3041](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3041); restrictive schema at [fitting.py:3216](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3216).

   The typed objects therefore are **not exactly the forms `run_fit` emits**. Tightening existing request acceptance would itself require a disclosed behavior change.

3. **MAJOR — finite recorded integers can still crash verification.**

   Starting with an honest Gaussian response, independently replacing any of these with `10**400` produced HTTP **500**:

   - `fitted_sub[0]`
   - `individual_peaks[0].y[0]`
   - `individual_peaks[0].params.amplitude.value`

   The float-only finiteness scan correctly leaves integers alone, but subsequent `float()` calls raise `OverflowError` before reaching the promised mismatch judgment.

   Evidence: free-parameter conversion at [fitting.py:3414](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3414); curve representability check at [fitting.py:3455](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3455); HTTP fallback at [app.py:1414](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:1414).

   The specific **large-ID** disposition is fixed: an unchanged response with `id = 10**400` verified consistently.

4. **MINOR — an earlier LA evaluation failure still hides a later stable-component mismatch.**

   In an LA/Gaussian response, changing only the Gaussian’s recorded center by `0.1` returned `mismatch / components`. Additionally doubling the LA’s recorded amplitude changed the answer to `unconfirmed / components`: verification exits at the first LA evaluation failure before checking the Gaussian.

   Evidence: [fitting.py:3437](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3437).

   This loses an independently decidable mismatch, but **does not make the forged record current**. I found no false-`consistent` exploit through this downgrade. Defer the uncertainty result until all stable evaluations have been checked.

5. **MINOR — the “huge integer” regression test does not exercise the original lossy-array defect.**

   The fixture’s first count is `176`, while the test substitutes `10000000000000001`. Even the lossy reader distinguishes those. I reinstated lossy `arr()` conversion in memory; this test case still returned its expected `mismatch / data`.

   Evidence: mutation at [test_seal_1a_verify.py:180](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:180); unscaled fixture at [test_seal_1a_verify.py:187](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:187).

   The implementation’s array fix itself passed the meaningful probe: honest `17600000000000000`, forged integer `17600000000000001` → `mismatch`.

Against the **seven original questions**:

1. **Pure refactor and measurements:** AST comparisons confirmed the extracted statements and their relative order: normalizer **8/8**, background **16/16**, model **5/5**. The app normalizer is the exact original suffix. Measurement summaries reproduce **187/202** original identity, control differences **10/15**, final **8/15 identical plus seven within rounding**, and post-round-1 **39/40 identical plus one LA within rounding**. These remain sampled evidence.

2. **Statistics:** The implementation matches the specified associations, reductions, denominators, floor order, AIC/BIC, RMSE and R-factor/null case. Internal decisions retain lmfit statistics. The committed measurements report zero change in all four compared statistics across **404 fits**.

3. **Verification:** Array comparisons are repaired, and statistics, support, bounds, background verdicts and seeds receive exact comparisons. Parameter handling still fails as finding 1 demonstrates. Ownership, expressions, request normalization, determinacy and linked-root support otherwise check out in the reviewed paths. LA-independent recorded-array relations now run before evaluations.

4. **Option (b):** Acceptance remains explicitly unproven. The non-recomputed fields match the memo: success, message, uncertainties, certificate, starts and required. I found no new claim that consistency establishes convergence.

5. **Provenance:** Environment hashing matches its stated sorted distribution-list input. Git status includes ordinary untracked files; ignored uploads and environments remain excluded. The template digest belongs to the compiled template object, and reference hashing uses the injected data. No additional defect found.

6. **Schemas and tests:** Apart from the ID mismatch, the inspected producer branches match the typed objects. A probe with a nonempty scattered-start alternative and a running required refit verified consistently. Findings 1–3 need regression coverage. The general all-lineshapes test also still unconditionally requires LA `consistent`, despite its permitted instability ([test_seal_1a_verify.py:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:59)).

7. **Design rules and remaining dispositions:** No verification tolerance was introduced. Finding 1 violates the single-reading requirement. `_component_required` now uses exact names, including all three direct test callers. The README’s unsupported residual-vector inference is removed.

**VERDICT: NO-GO.**
