**NO-GO.** I reproduced a false `consistent` result through `/api/verify-fit`, an honest-record verification failure, and non-arithmetic errors hidden by the LA fallback.

The checkout is `966fe00`; its only change after `3987469` is the round-2 prompt. I kept it unchanged, inspected the tests and measurements, and ran bounded in-memory probes. I did not run pytest.

1. **BLOCKER — array conversion still accepts numerically different records as `consistent`.**

   `arr()` checks that elements are numbers, then converts them to float64 **before comparison**. Distinct JSON integers can therefore round to the expected value.

   Reproduced with an honest Gaussian fit, independently changing only:

   | Field | Original value | Forged JSON integer | Route result |
   |---|---:|---:|---|
   | `counts[0]` | `10000000000000000` | `10000000000000001` | HTTP 200, `consistent` |
   | `fitted_y[0]` | `10000000000000000` | `10000000000000001` | HTTP 200, `consistent` |
   | `fitted_sub[28]` | `11665290395760756` | `11665290395760757` | HTTP 200, `consistent` |
   | Component `y[28]` | `11665290395760756` | `11665290395760757` | HTTP 200, `consistent` |

   These are unequal numbers, unlike `285` and `285.0`. `_same` distinguishes them; the array path loses that distinction.

   Evidence: [fitting.py:3278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3278), [fitting.py:3387](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3387), [fitting.py:3392](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3392). Compare recorded numbers without a lossy conversion, or establish that conversion preserves each number exactly.

2. **MAJOR — the LA fallback hides failures unrelated to evaluator arithmetic.**

   Starting from an honest LA response that verified `consistent`, I independently changed:

   - `statistics.chi_square` to `"garbage"`;
   - `statistics.n_data` from `101` to `102`;
   - `statistics` to `{}`;
   - `support.supported` to integer `1`;
   - `support` to `{}`.

   Every mutation returned **`unconfirmed`**, attributed to LA’s evaluator. Missing keys, wrong types and an incorrect data count cannot arise from convolution rounding.

   Statistics and support validation use whole-object comparisons inside `_verify_curves`; the exception handler then downgrades every failure carrying those check names. The request-wide fallback also covers components whose own evaluator is stable.

   Evidence: [fitting.py:3371](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3371), [fitting.py:3398](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3398), [fitting.py:3418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3418).

   Validate structure, types and arithmetic-independent invariants outside that fallback. LA-only inclusion is supported by the current evidence; DS+G and other shapes remain 1b’s measurement. The problem here is the fallback’s scope.

3. **MAJOR — the finiteness scan crashes on an honest, accepted integer ID.**

   A Gaussian request with `id = 10**400` successfully produced a response. Verifying that unchanged response through the route returned **HTTP 500**.

   `_non_finite` calls `math.isfinite` on Python integers. This finite integer overflows the implicit conversion to float, raising `OverflowError`. The producer accepts the ID; the new verifier cannot judge its response.

   Evidence: [fitting.py:3176](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3176), [app.py:1413](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:1413). Integer finiteness needs no float conversion.

4. **MINOR — the README correction retains an unsupported inference.**

   It now correctly says the residual vectors were not compared, but immediately claims that none of the 404 fits had its last evaluation away from the returned parameters. The recorded scalar-statistic equality does not establish that.

   Evidence: [README.md:20](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/findings/seal-1a/README.md:20). Delete or narrow the remaining “none of the 404 fits is such a case” clause.

The eight dispositions check out as follows:

| Disposition | Assessment |
|---|---|
| **1. Exact ownership** | Fixed on the production seal paths: response parameters, support, scattered-start solutions, required removal and verification use component-owned names. Every recorded parameter value is checked after constraint evaluation. An overlapping-ID probe verified correctly, with both starts and required refit running. |
| **2. Typed schema / non-finite values** | Numeric strings, boolean substitutions, stderr types and ordinary NaN/Infinity cases are addressed. Findings 1 and 3 remain. |
| **3. Negative zero in links** | Fixed for both splitting and area ratio. An honest `-0.0` splitting response verified after respelling the request as `0`. |
| **4. Unstable lineshapes** | Known LA arithmetic failures now become `unconfirmed`; finding 2 prevents accepting the implementation as complete. |
| **5. Compiled-template digest** | Fixed. The digest belongs to the compiled object. An in-memory reload/interleaving probe preserved the old template’s digest while loading a new version and another template. |
| **6. Reversed bounds** | Fixed in the reviewed path. The copied parameters supply effective roles and held values; seed derivation still uses the start. An honest reversed-center/reversed-width response verified. |
| **7. Stronger tests** | The statistic-substitution test now meaningfully checks required/starts/certificate/parameters. Expression-value, caller-seed, determinacy, bounds, floor and null tests address the named gaps. None covers the three reproduced failures above. |
| **8. README** | Improved, with the remaining qualification in finding 4. |

The requested `startswith` search still finds parameter membership at [fitting.py:2359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2359), but only in `_component_required`’s compatibility fallback; its production caller supplies `removed_names`. No `startswith` remains in `app.py`. Existing parameter-prefix readers remain in `autofit/confidence.py:77`, `autofit/engine.py:659,1301`, `autofit/methods/bayesian_exchange_mc.py:531`, and `autofit/methods/ic_model_comparison.py:234`. Those Auto-Fit files are unchanged by this unit; the repository-wide claim “exact everywhere” would be too broad.

Against the **seven original questions**:

1. **Refactor and identity:** The extracted normalizer/model statements match their predecessors; background assembly preserves the original operations. I found no additional refusal-wording or precedence change beyond the disclosed fix. The measurement summaries reproduce: **187/202** original identity; control differences on **10/15**; final comparison **8/15 identical**, seven within the existing comparator; round-1 fixes **39/40 identical**, one LA case within rounding. These are sampled evidence, not universal identity.
2. **Statistics:** `_fit_statistics` implements the required associations, reductions, denominators, floor ordering, AIC/BIC, RMSE and R-factor/null behavior. Internal decisions retain lmfit statistics, including required-refit `chi2_with`. The committed measurements report zero difference in the four compared statistics on **404 fits**.
3. **Verification:** Ownership, roles, expressions, background, seeds, determinacy and linked-root support are substantially implemented. Findings 1–3 prevent the promised verification contract.
4. **Option (b):** The acceptance distinction remains honest. Success, message, uncertainties, certificate, starts and required are recorded assertions; consistency does not prove convergence or a minimum.
5. **Provenance:** Environment hashing matches the sorted distribution-list contract. Git status includes ordinary untracked files while ignored uploads/venv files remain excluded. Template-object provenance is repaired; reference hashing uses the injected value.
6. **Tests:** The strengthened tests improve coverage substantially. Add lossless-number, large-integer-ID and LA structural/invariant cases. The recorded full-suite results are for the earlier revision; the reported targeted passes do not cover these failures.
7. **Design rules:** No explicit numerical tolerance was introduced. Nevertheless, array coercion creates an unintended equivalence between different recorded numbers—the remaining “two readings” defect.

**VERDICT: NO-GO.**
