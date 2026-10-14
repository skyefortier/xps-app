**NO-GO. I reproduced an honest-record rejection and three verification paths that return HTTP 500.** I found no remaining false-`consistent` result in the probes below.

Reviewed `4c2cfde`; HEAD `ec71deb` adds only the round-3 prompt. The checkout remains unchanged. Validation used source/AST comparisons, committed measurements, and bounded in-memory probes through the actual routes, substituting only session-array loading. I did not run pytest.

1. **MAJOR — the new ID schema rejects responses the producer honestly emits.**

   `_typed(..., "id")` permits only strings and non-boolean integers. The fit request reader does not impose that restriction, and `_certificate_report` copies the accepted component ID into its movement records.

   Using the well-posed fixture’s first component with Gaussian shape:

   | Request component ID | `/api/fit` | Verification of unchanged response |
   |---|---|---|
   | `true` | HTTP 200, `success: true` | `mismatch/schema` |
   | `false` | HTTP 200, `success: true` | `mismatch/schema` |
   | `null` | HTTP 200, `success: true` | `mismatch/schema` |
   | `1` | HTTP 200, `success: true` | `consistent` |

   All three failures say **“certificate is not of a response’s form.”** The same null-ID response verifies `consistent` under `3987469`, confirming this is introduced by round 2.

   Evidence: request validation at [app.py:104](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:104), producer at [fitting.py:3041](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3041), restriction at [fitting.py:3216](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3216).

   The verifier’s ID schema must match the producer’s accepted domain. Tightening the existing fit API instead would be a separate behavior change requiring explicit treatment.

2. **MAJOR — finite integers still escape the verdict path through overflowing conversions.**

   Starting from a consistent Gaussian response, independently replacing any of these with `10**400` produces **HTTP 500**, “Internal verification error”:

   - `fitted_sub[0]`
   - `individual_peaks[0].y[0]`
   - A free amplitude’s `params.amplitude.value`

   The curve representability guard itself calls `float(v)` without handling overflow. Free parameters likewise convert before their later exact comparison. `_non_finite` correctly recognizes these integers as finite, but the subsequent checks cannot judge them.

   Evidence: [fitting.py:3455](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3455), [fitting.py:3414](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3414), route exception handling at [app.py:1413](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:1413).

   An unrepresentable recorded value should produce a mismatch, including when conversion overflows.

3. **MINOR — LA uncertainty can still suppress a later stable-component mismatch.**

   Component evaluation stops immediately at the first unstable mismatch. I forged both curves in an LA-first/Gaussian-second response by multiplying them by `1.1`, then recomputed their areas, model sum, fitted curve, residuals, statistics, and support. Verification returned **`unconfirmed/components`** at LA, never reaching the independently false Gaussian identity.

   Evidence: [fitting.py:3437](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3437).

   Defer the uncertainty result until all independently decidable checks finish. This is a classification/order defect; **it does not make the forged record current**, so it is not another acceptance blocker.

4. **MINOR — the “huge integer” regression test does not exercise the repaired rounding hole.**

   Its fixture has `counts[0] == 176.0`; the mutation replaces that with `10000000000000001`. Even the old lossy verifier rejects this enormous difference. I loaded `3987469` in memory and confirmed that it passes this negative case.

   Evidence: [test_seal_1a_verify.py:179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:179), [fixture:187](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:187).

   Use an honest value and unequal integer that convert to the **same** float, and cover the affected array families.

The six round-2 dispositions:

| Disposition | Assessment |
|---|---|
| **1. Lossy numbers** | The false-equality hole is fixed in my probes. Scaling counts/amplitudes by `1e14`, unequal integers sharing the honest float were rejected in counts, component curves, free parameters, areas, statistics, and support. Bounds and background verdict use exact typed equality; seeds compare integers directly. Free values retain their original number for the post-conversion comparison. Overflow remains finding 2. |
| **2. LA scope** | Recorded-array relationships now run first and remain exact. Only evaluation identities downgrade. Finding 3 remains; I found no resulting false `consistent`. |
| **3. Typed objects** | Starts, required/refit outcomes, not-run branches, certificate fields, support, and statistics otherwise match the inspected producer branches. The shared ID restriction creates finding 1. |
| **4. Huge integer ID** | Fixed: an honest `10**400` ID verified `consistent`. That fix does not cover huge curve/parameter numbers. |
| **5. Required ownership** | Fixed. `_component_required` accepts exact parameter names; the production caller and all three direct tests supply them. |
| **6. README inference** | Fixed. The statistics discussion now explicitly disclaims conclusions about unmeasured residual vectors. |

Against the original seven questions:

1. **Pure refactor:** AST comparison found every extracted statement in its original relative order for all three fitting helpers; the app reader is the exact original suffix. The separately disclosed wording, ownership, and signed-zero changes remain identifiable. Measurements reproduce **187/202 identical**, control differences on **10/15**, and final **8/15 identical plus seven passing the existing comparator**. The post-round-1 file records **39/40 identical**, with the remaining LA case passing that comparator. These are sampled evidence, not universal identity.

2. **Statistics:** The association, NumPy reduction, denominators, reduced-chi-square-before-floor order, AIC/BIC, RMSE, and null R-factor match V6.6. Internal decisions retain lmfit’s values, including required-refit `chi2_with`. The summarizer confirms zero measured difference in the four compared statistics across **404 fits**.

3. **Verification:** Request normalization, starting-parameter seed derivation, exact ownership, effective roles/bounds, held values, expressions, determinacy, whole background/verdict, curves, areas, associations, statistics, and linked-root support are present. Findings 1–3 prevent a clean pass.

4. **Option (b):** The consistency-versus-acceptance language remains honest. Unrecomputed fields are `success`, `message`, uncertainties, `certificate`, `starts`, and `required`; consistency does not establish convergence.

5. **Provenance:** Environment hashing matches its stated metadata inputs. Git status includes ordinary untracked files; ignored uploads and environments remain excluded. The template digest belongs to the compiled object; an in-memory reload/multiple-template probe preserved each object’s correct digest. Reference hashing uses the injected object.

6. **Tests:** Coverage improved, but finding 4 does not guard the original blocker. Missing cases include accepted boolean/null IDs, overflowing numeric conversions, and stable failures after an unstable component. Supplied suite results were not independently rerun.

7. **Design rules:** No verification tolerance or new data-scaled cutoff was introduced. Original recorded numbers survive comparison; the remaining defects need schema alignment, safe conversion rejection, and check ordering.

**VERDICT: NO-GO.**
