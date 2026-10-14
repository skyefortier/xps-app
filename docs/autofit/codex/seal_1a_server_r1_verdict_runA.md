**NO-GO: I reproduced a false `consistent` result and a false `mismatch`.** The statistics implementation and shared request reader look correct, but the verifier does not yet enforce the stated contract.

I reviewed the diff and committed measurements, reran the read-only summariser, and ran bounded in-memory probes. I did not run pytest or modify files; suite results below remain the supplied results.

1. **BLOCKER — overlapping ID prefixes allow contradictory parameter values to verify.**  
   With Gaussian IDs `"a"` and `"a_b"`, the first component also echoes `pa_b_center` as `params.b_center`, because extraction uses `startswith(prefix)`. Verification collects both copies and assigns them sequentially; the later copy wins. It never checks the earlier free value against the final parameter.

   Reproduced: changed only the first component’s `b_center` from approximately `288.0` to `288.1`, leaving the second component, curves, areas and statistics untouched. Result: **`consistent`**. This O cannot be the server’s response: its two representations of one parameter disagree.

   Evidence: [fitting.py:2860](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2860), [fitting.py:3234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3234), [fitting.py:3266](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3266). Every echoed value must agree with the parameter actually evaluated, including duplicated free values.

2. **MAJOR — schema validation accepts objects the server cannot emit as those fields.**  
   Independently reproduced `consistent` after replacing:
   - Every `counts` number with its decimal **string**.
   - `params.area.stderr` with `{"not": "a number"}`.
   - A parameter’s `stderr` with **NaN**.

   `arr()` converts before validating types; ordinary stderr checks omit finiteness; area validation checks only its keys. These are schema checks, not recomputation of uncertainty, so option (b) does not excuse their omission.

   There is also no general finite-number validation for statistics/support. A finite-input probe with counts `1e200` produced `rmse = Infinity` and `support.delta_chi2 = NaN`; its Python JSON round-trip verified `consistent`. Thus the finite-number contract is not enforced even when every array is finite.

   Evidence: [fitting.py:3182](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3182), [fitting.py:3245](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3245), [fitting.py:3258](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3258), [fitting.py:3293](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3293).

3. **MAJOR — signed-zero normalization can make an honest record stale.**  
   Reproduced a linked Gaussian request with `splitting: -0.0`: its response verified `consistent`. Changing only that request number to `0`, as JavaScript serialization does, produced **`mismatch / seed`**.

   Splitting is interpolated into an expression string, so `" + -0.0"` survives numeric canonicalization and changes the seed. With a caller seed, the expression-role comparison still distinguishes those strings. This is inherited expression/seed behavior exposed by the new verifier, not a refactor-induced solver change.

   Evidence: [fitting.py:1615](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:1615), [fitting.py:2130](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2130), [fitting.py:3217](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3217).

4. **MAJOR — known evaluator instability is classified as mismatch, contrary to V6.5.**  
   The README explicitly acknowledges honest LA records may fail exact verification in another worker. The implementation has no unverifiable-shape path: unequal reevaluation becomes `mismatch`. The unit plan expressly permits that until 1b, whereas the approved design requires **UNCONFIRMED** for a shape that cannot be verified exactly. V6.22 preserves that requirement.

   This limitation is disclosed honestly, but disclosure does not resolve the false-STALE behavior.

   Evidence: [fitting.py:3282](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:3282), [unit plan:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/superpowers/plans/2026-10-13-seal-1a-server.md:59), [README:48](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/findings/seal-1a/README.md:48), [design:907](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:907).

5. **MAJOR — the page digest belongs to a template name, not the compiled template being rendered.**  
   Under overlapping requests with auto-reload: request A obtains the old compiled template; request B reloads the name and overwrites `digests["index.html"]`; A then reads B’s digest and renders its old template.

   An in-memory probe reproduced that interleaving: old content carried the new source’s hash. Sequential reloads and loading another template worked correctly. This race does not arise from concurrent page requests in the documented synchronous production workers, but the unqualified per-render provenance claim is false under threaded serving. Attach the digest to the returned compiled template.

   Evidence: [app.py:239](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:239), [app.py:869](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/app.py:869).

Answers to the seven questions:

1. **Pure refactor:** I found no additional change to ordinary fit computation, request interpretation, refusal wording or refusal precedence in the four extractions. The separate `bfca83a` wording change is explicitly logged and tested. The measurements support numerical preservation on their sampled successful requests; they cannot establish every refusal or universal byte identity. The reported counts reproduce: **187/202** identical; control differs on **10/15**; final comparison identical on **8/15**, remaining seven within the existing same-fit standard. The README discloses these limits reasonably. Its assertion that the last residual evaluation “IS the returned model” exceeds what equal scalar statistics establish: the generator never compares those residual vectors.

2. **Statistics:** `_fit_statistics` implements the specified association, NumPy reduction, roles count, denominator, **redchi before flooring**, floored chi-square, AIC/BIC, RMSE and R-factor/null case. Internal restart ranking, certification, scattered starts and the required refit retain lmfit’s values; notably `chi2_with` still receives `float(result.chisqr)` at [fitting.py:2831](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/fitting.py:2831). The committed results correctly report zero change in the four compared statistics across both sets of 202 fits. The overflow/schema problem above remains.

3. **Verification:** Outside the findings, the implementation checks top-level/component keys, order, IDs, shapes, parameter names, array dimensions, data, method, shift, seeds and seed source. It uses the fit routes’ normalizer and derives seeds from **starting** parameters. Roles use the same model builder, preserving widened held limits and requested bounds rather than DE-generated search sides. Held values exclude expressions; free values are installed before constraint updates, allowing reversed chains. Determinacy, complete background assembly/verdict, component curves, trapezoidal areas, composite evaluation, array associations, statistics and linked-root support are present. Ordinary `285` versus `285.0` comparisons work. Integer and string IDs are preserved as distinct request/response values; mixed IDs that collide as prefixes are refused. The underscore-prefix and signed-zero cases above fail. Whole-`software` comparison is the specified conservative rule; differing software correctly yields `unconfirmed`, although that comparison is not provenance authentication.

4. **Option (b):** The route, verifier docstring, plan and CLAUDE.md explicitly distinguish consistency from acceptance. I found no promise that `consistent` proves convergence or a minimum. The unrecomputed list matches the amended memo: `success`, `message`, uncertainties, `certificate`, `starts`, `required`. Background verdict and support correctly remain recomputed. Structural validation of recorded fields still needs fixing.

5. **Provenance:** `env_sha256` deterministically hashes sorted installed `Name==version` lines, joined with newlines and no terminal newline. It identifies that metadata list, not native binaries or executed code. `git_dirty` includes ordinary untracked files but excludes ignored files. The production checkout’s status was clean; `uploads/`, `venv/` and `.claude/` are ignored, so uploads do not continually mark it dirty. The loader’s `BaseLoader.load` path correctly passes through its digesting `get_source`; sequential caching/reload and separate template names work. The race above breaks per-render identity. `reference_sha256` hashes canonical JSON of the same `legacy` object passed for injection. I found no ordinary production page-serving change beyond the added meta tag.

6. **Tests — MINOR coverage deficiencies, with a materially misleading test name:**  
   [test_internal_decisions_keep_their_own_statistic:92](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a/tests/test_seal_1a_server.py:92) checks only that the required refit ran and `chi2_with > 0`; it would pass if the reported statistic were substituted. It does not establish its named guarantee.

   The tamper suite has useful one-ULP checks, but an implementation missing the **expression-value check** could still pass: its `"expr"` mutation tests the role string, while chain tests only exercise honest responses. Likewise, caller-seed rejection, out-of-bound free values with coherently regenerated outputs, and determinacy need negative cases. Missing cases include all reproduced failures, zero-residual flooring, zero-denominator R-factor, and reload interleaving. The supplied passing suites do not close these gaps.

7. **Design rules:** No new numerical tolerance is introduced in verification. Existing statistical floors and same-fit measurement tolerances retain their stated purposes. However, string-to-number coercion of O introduces an extra reading of a response field, duplicated free parameters permit conflicting readings, and signed-zero expression formatting violates the intended spelling-independent interpretation.

**VERDICT: NO-GO.**
