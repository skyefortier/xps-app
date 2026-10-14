**The unit is not ready to ship.** I confirmed both false consistency and false STALE cases. The helper extraction and statistics arithmetic look correct; the verifier and provenance guarantees need fixes.

I kept the checkout unchanged. I inspected the recorded suite results, reran the read-only measurement summarizer, and used bounded, in-memory probes—not pytest.

1. **Pure refactor: yes, with the declared wording exception.**

   AST comparison confirms that `_normalise_fit_kws`, `_assemble_background`, and `_build_model` contain the original statements in their original order, and `_normalise_fit_request` is the unchanged suffix of `_prepare_fit_request`. Existing fit-route normalization and refusal precedence remain intact. The changed lineshape refusal is the separately logged bfca83a change, not an accidental refactor change. See [fitting.py:2393](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2393), [app.py:66](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:66), and [fitting.py:1528](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1528).

   The measurement counts check out: **187/202 identical**, control differences on **10/15**, final comparison **8/15 identical and 7/15 passing the existing same-fit comparator**. This supports the refactor, but cannot establish every refusal or universal identity. The README identifies the comparator and limitations, although “none differs beyond rounding” must be read with that comparator’s exclusions: stderr, messages, and some certificate history are not compared.

2. **Statistics: the implementation matches V6.6.**

   [fitting.py:2977](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2977) uses the required residual association, NumPy reduction, unfloored reduced chi-square, subsequent chi-square floor, and lmfit AIC/BIC formulas. RMSE divides by the sample count; R-factor returns null for a zero denominator. The varied-parameter count excludes expressions.

   Internal decisions still read lmfit’s values: restart ranking, certification, scattered starts, and specifically the required refit’s `float(result.chisqr)` at [fitting.py:2831](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2831).

   Both JSONL files confirm **202/202 identical reported statistics per method**, zero measured change, and 404 in-process consistent verifications. The README’s stronger assertion that the minimizer’s last residual evaluation *is* the returned model is not established by this generator: it compares aggregate statistics and `best_fit == fitted_sub`, not the two residual arrays. Report the measured equality without inferring that additional identity.

3. **Verification: there are blocking correctness failures.**

   **BLOCKER — overlapping prefixes permit contradictory numerical parameter records.**  
   Parameter membership uses `startswith(prefix)`. With valid string IDs `"1"` and `"1_x"`, the first peak’s response contains `x_center`, etc., belonging to the second peak. The verifier queues those free values twice; the second occurrence overwrites the first, and the first recorded value is never checked again.

   I produced an honest, consistent two-Gaussian response, changed only the first peak’s `params.x_center.value` to a different in-bounds value, and verification still returned **`consistent`**. This is a numerical contradiction, not an exempt acceptance statement. See [fitting.py:3234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3234), [fitting.py:3257](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3257), and [fitting.py:3266](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3266).

   **MAJOR — honest fits with reversed bounds become STALE.**  
   `_make_peak_params` assigns bounds directly; lmfit subsequently normalizes reversed bounds when copying parameters for fitting. The verifier compares against the earlier, unnormalized bounds.

   Reproduced for center, FWHM, and amplitude. For example, `center_min=287, center_max=283` produced a successful fit reporting bounds `[283,287]`; the actual verification route returned HTTP 200 **`mismatch/roles`**. See [fitting.py:1601](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1601) and [fitting.py:3247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3247). The verifier must reproduce the fitter’s effective roles while preserving the existing starting-parameter seed derivation.

   **MAJOR — schema checking accepts records the server cannot emit.**  
   Confirmed independently against a valid response:

   - Replacing `fitted_y` numbers with numeric strings remains `consistent`.
   - Replacing charge shift `0.0` with `false` remains `consistent`.
   - Replacing `support.supported` with integer `0`/`1` remains `consistent`.
   - Replacing area stderr with `"garbage"` remains `consistent`.
   - Parameter stderr accepts NaN and Infinity.

   Arrays are coerced before checking; several other fields use Python equality, which equates booleans and numbers. Area stderr has no value validation. These are schema issues even where the underlying uncertainty is deliberately not recomputed. See [fitting.py:3182](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3182), [fitting.py:3243](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3243), and [fitting.py:3258](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3258).

   Non-finite derived fields also escape validation. A finite-input probe produced `rmse=Infinity` and `support.delta_chi2=NaN`; its normal Python JSON round-trip verified consistent. Parsing NaN into a fresh float instead produced `mismatch/support`: dictionary equality can depend on Python’s shared JSON NaN object. Neither outcome is an adequate finite/schema contract. See [fitting.py:3293](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3293) and [fitting.py:3314](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3314).

   **MAJOR — signed-zero normalization fails inside generated expressions.**  
   Ordinary `285` versus `285.0` verifies correctly. However, a linked request with `splitting=-0.0` generates an expression containing `-0.0`. Re-serializing that request with splitting `0` changes the expression text and derived seed. I confirmed **`mismatch/seed`** for the otherwise unchanged honest result. With a caller seed, the expression-role comparison remains vulnerable. See [fitting.py:1615](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1615) and [fitting.py:2130](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2130).

   **MAJOR — the documented unstable-evaluator outcome contradicts V6.5.**  
   The plan explicitly permits non-bit-stable shapes to return `mismatch` until 1b. The approved design says these are **UNCONFIRMED, never STALE**. The verifier has only exact curve comparisons, without that distinction. The README already acknowledges the LA risk. Deferring the determinism work does not justify assigning an honest record the wrong state. See [unit plan:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/superpowers/plans/2026-10-13-seal-1a-server.md:59) and [fitting.py:3282](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3282).

   The remaining checks are substantially implemented correctly:

   | Check | Assessment |
   |---|---|
   | Keys, component count/order, IDs, shapes, parameter names | Explicit checks exist; type coercion and prefix overlap weaken them. |
   | Request, data, method, shift | Uses the fit routes’ reader and shifted arrays. Session ID is correctly transport-only. |
   | Seed | Correctly derived from starting parameters before installing O’s free values; caller seed/source checked. |
   | Roles and held values | Shared construction handles widened held limits and linked children; reversed bounds are the exception above. |
   | DE generated bounds | Comparing request bounds matches the producer’s suppression of generated search sides. |
   | Expressions | All free values are installed before `update_constraints`; chains can resolve independently of request order. |
   | Determinacy | Present and based on the effective parameter count and finite data count. |
   | Background | Whole shared assembly and whole verdict are compared. |
   | Curves, areas, associations, statistics | Recomputed in the required associations, without tolerance. |
   | Support | Same helper and transitive root-following rule; schema/non-finite issues remain. |
   | Different software | Whole-object comparison correctly produces `unconfirmed` for ordinary well-typed differences. It is not authentication. |

   Integer versus string IDs are preserved by the producer; changing only O’s ID correctly fails. That is distinct from the overlapping-string-prefix defect.

4. **Option (b): the acceptance disclaimer is honest.**

   The route, verifier docstring, unit plan, and CLAUDE.md explicitly distinguish consistency from acceptance. They do not promise that a consistent record converged or reached a minimum.

   The non-recomputed list matches the memo: **success, message, uncertainties, certificate, starts, required**. Background verdict and support are recomputed. A coherent non-minimum with fabricated acceptance can therefore be consistent by design; that is separate from the contradictory-record failures above.

5. **Provenance: environment identity is reasonable; page identity is not guaranteed per render.**

   `env_sha256` hashes sorted installed-distribution `Name==version` strings joined with newlines, without a trailing newline. That is deterministic for the same discovered distribution metadata, not a hash of native artifacts or executed code.

   `git_dirty` now includes ordinary untracked files. Ignored `uploads/`, `venv/`, `.claude/`, bytecode, etc. do **not** dirty production merely by existing. This is an import-time snapshot. See [fitting.py:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:59).

   **MAJOR — page digest belongs to a mutable name entry, not the rendered template.**  
   One request can obtain compiled template A; another auto-reloading request can load B and overwrite `digests["index.html"]`; the first request then renders A with B’s digest. I reproduced the corresponding loader interleaving in memory. See [app.py:239](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:239) and [app.py:869](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:869).

   Ordinary sequential loading, cached loading, and separate template names work. The wrapper’s `BaseLoader.load` path does call its `get_source`, so it captures the source on the normal Flask loader path. The production sync-worker configuration narrows the race’s exposure, but does not support the unconditional per-render claim. Associate the digest with the compiled template object.

   `reference_sha256` hashes the same `legacy` value passed into rendering, using canonical JSON. Normal page serving and the static fallback otherwise remain intact.

6. **Tests: useful coverage, but several named guarantees are not tested.**

   **MAJOR — `test_internal_decisions_keep_their_own_statistic` does not test its claim.**  
   It asserts only that the required check ran and `chi2_with > 0`. Substituting the reported statistic—or an arbitrary positive number—would pass. See [test_seal_1a_server.py:92](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_server.py:92).

   Likewise, deleting the expression-*value* comparison can leave the suite passing: tests change expression metadata, but never forge a linked parameter’s computed value. The successful grandchild case does not test rejection of contradictory expression values. See [test_seal_1a_verify.py:131](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_verify.py:131).

   Missing critical cases include the confirmed failures above, a linked child whose independent support differs from its root, and DE’s retained generated-box result. Statistics tests need a case where lmfit’s stored statistic differs from the returned-array statistic, plus zero-residual floor ordering and zero-denominator R-factor cases. The page tests cover cache-without-reload, not overlapping reloads.

   The recorded **1499 Python passes and 647 JS passes** are credible suite results, but do not establish these missing guarantees.

7. **Design rules: no new numerical tolerance, but second-reading defects remain.**

   Exact verification introduces no tolerance or data-scaled threshold. The measurement script’s existing same-fit tolerance is not used to establish consistency.

   Shared readers successfully avoid duplicating request and background interpretation. However, comparing pre-lmfit bounds against post-lmfit bounds, coercing recorded strings into numeric arrays, and permitting overlapping parameter ownership violate the intended “two readings” discipline. Those need structural fixes, not tolerances.

**VERDICT: NO-GO.**
