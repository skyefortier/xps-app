**NO-GO. I reproduced two false `consistent` cases and confirmed that the LA fallback hides non-arithmetic mismatches.**

Reviewed implementation `3987469`. Actual HEAD is `966fe00`, which adds only the round-2 prompt. The checkout remains unchanged. I used source/AST comparisons, the committed measurement summarizer, and bounded in-memory probes—including the actual verification route. I did not run pytest.

1. **BLOCKER — numeric arrays still undergo a lossy conversion before comparison.**

   `arr()` validates JSON numeric types, then converts every value to `float64`. Distinct JSON integers can therefore become equal before verification.

   Reproduced with the Gaussian fixture, counts and initial amplitudes scaled by `1e14`, background `none`:

   - Honest `O.counts[0]`: `17600000000000000`.
   - Changed only that entry to integer `17600000000000001`.
   - Both the honest and forged records returned HTTP 200 **`consistent`**.

   Python’s exact numeric equality—and this implementation’s `_same`—distinguishes those values. The conversion erases the difference. This affects every array checked through `arr()`.

   Evidence: [fitting.py:3278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3278), [fitting.py:3283](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3283).

   Compare recorded numbers exactly against the computed values before accepting any conversion that changes their value.

2. **MAJOR — nested acceptance fields bypass the promised JSON-type validation.**

   `certificate`, `starts`, and `required` are checked only for being dictionaries or null. Starting from an honest, consistent response containing all three, I independently changed:

   - `certificate.certified`: `true` → `"false"`.
   - `starts.ran`: `true` → `"false"`.
   - `required.ran`: `true` → `"false"`.

   Each still returned **`consistent`**. These probes preserved every other field and key.

   Option (b) permits an unproven boolean assertion; it does not establish that a string is a valid boolean assertion. Validating its type requires no refit or acceptance recomputation. The claim that every field receives JSON-type validation remains false.

   Evidence: [fitting.py:3244](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3244), [unit plan:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/superpowers/plans/2026-10-13-seal-1a-server.md:59).

3. **MAJOR — the LA exception classifies whole check categories as arithmetic uncertainty.**

   Against an honest mixed LA/Gaussian response that initially verified consistent, these independent mutations returned **`unconfirmed`**:

   - Replace `statistics` with `{}`.
   - Change `statistics.n_data` to `999`.
   - Change `support.supported` to text.
   - Corrupt the Gaussian component’s curve.

   None requires resolving LA rounding. The exception handler knows only the request contains LA and the failure’s broad check name. Statistics/support schema errors and failures of independently stable components consequently lose their `mismatch` classification.

   Evidence: [fitting.py:3371](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3371), [fitting.py:3398](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3398), [fitting.py:3418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3418).

   Validate structure, types, counts, and independently checkable relationships before applying evaluator uncertainty. Restrict that uncertainty to computations actually dependent on the unstable evaluator.

Against the original seven questions:

1. **Pure refactor and identity:** The four extractions check out. AST comparison found the original statements in their original relative order for `_normalise_fit_kws`, `_assemble_background`, and `_build_model`; the app request reader is the exact original suffix. The separately disclosed wording, ownership, and signed-zero changes remain identifiable.

   The measurements reproduce: **187/202 identical**, control differences on **10/15**, final comparison **8/15 identical plus seven passing the existing same-fit comparator**. The post-fix file contains **39/40 identical**, with one LA result passing that comparator. These establish the sampled results, not universal identity.

   **MINOR wording:** The README correctly says residual vectors were not compared, but its remaining “none of the 404 fits is such a case” parenthetical should explicitly mean *no measured statistic difference*, rather than claiming where the minimizer’s last evaluation occurred. [README:20](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/findings/seal-1a/README.md:20).

2. **Statistics:** `_fit_statistics` matches the specified association, NumPy reduction, denominators, reduced-chi-square-before-floor ordering, AIC/BIC, RMSE, and null R-factor case. Internal decisions retain lmfit’s statistics, including the required refit’s `float(result.chisqr)`. The committed measurements report zero difference in all four compared statistics across **404 fits**. [fitting.py:2988](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2988), [fitting.py:2856](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2856).

3. **Verification and dispositions 1–4, 6:** Exact component ownership now covers response parameters, support, scattered starts, required removal, and verification. My overlapping-ID probe also exercised starts and required removal successfully. Every recorded parameter value is checked against the evaluated value.

   Reversed bounds verified consistently. A linked `-0.0` splitting remained consistent after respelling it as `0`; both splitting and ratio receive the normalization. Forged expression values returned `mismatch/expressions`. Recursive non-finite scanning correctly returned `unconfirmed/non_finite`, including inside otherwise exempt objects.

   Request normalization, starting-parameter seed derivation, roles, held values, determinacy, background assembly/verdict, curve associations, areas, and linked-root support are present. Whole-software comparison remains conservative and unauthenticated as intended. The three findings above prevent an overall pass.

   Including **LA alone** is supported by the supplied evidence. I found no basis here to add DS+G merely because it uses FFTs; its broader measurement remains 1b’s work. The defect is the fallback’s scope.

   **Prefix search:** Prefix-based membership does remain:
   - `_component_required`’s compatibility fallback at [fitting.py:2359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2359); the production caller supplies exact `removed_names`.
   - [autofit/confidence.py:77](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/autofit/confidence.py:77).
   - [autofit/engine.py:659](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/autofit/engine.py:659), using longest-prefix ordering, and [autofit/engine.py:1301](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/autofit/engine.py:1301).
   - [bayesian_exchange_mc.py:531](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/autofit/methods/bayesian_exchange_mc.py:531) and [ic_model_comparison.py:234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/autofit/methods/ic_model_comparison.py:234).

   Those are existing separate paths; I did not establish a remaining seal-verifier ownership exploit through them.

4. **Option (b):** The consistency-versus-acceptance language is honest. The unrecomputed list remains `success`, `message`, uncertainties, `certificate`, `starts`, and `required`. Finding 2 concerns their schema, not proof of their truth.

5. **Provenance and disposition 5:** The digest race is fixed. The loader matches Jinja’s load sequence and attaches the digest to the returned template. In-memory probes passed old/new overlapping template references, multiple names, and bytecode-cache reuse. The route reads that object’s digest. [app.py:244](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:244), [app.py:879](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:879).

   Environment hashing and reference hashing match their stated inputs. Git status includes ordinary untracked files; ignored uploads, virtual environments, and `.claude` files do not dirty it merely by existing.

6. **Tests and disposition 7:** The internal-statistics test now meaningfully replaces reported statistics with nonsense and compares required checks, starts, certificates, and parameters. Expression-value, caller-seed, bounds, determinacy, floor/null, and digest regression tests target the stated defects.

   Missing cases are the three reproduced failures above. The LA test’s non-arithmetic negative case checks only the seed, leaving statistics/support structure and mixed-shape independence uncovered. Its unconditional honest-LA `consistent` assertion also remains vulnerable to the instability the fallback is intended to accommodate. [test_seal_1a_verify.py:311](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:311).

7. **Design rules:** No new verification tolerance or data-scaled cutoff was introduced. However, finding 1 retains a second, lossy reading of recorded numbers. The LA fallback avoids tolerances but fails to preserve independently decidable mismatches.

**VERDICT: NO-GO.**
