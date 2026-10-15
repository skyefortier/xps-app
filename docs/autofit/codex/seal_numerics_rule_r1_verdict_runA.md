The commit-only regression is fixed, but the change does **not fully implement the owner’s rule**. I found MAJOR gaps in the numerics guard and recheck behavior. No BLOCKER finding.

1. **Owner rule: correct for a fresh, readable verification; incomplete overall.**

   Valid differences in commit, checkout state, or environment digest no longer prevent confirmation. `_verify` runs before `consistent` is returned; I found no new path that confirms differing curves or statistics. Acceptance remains recorded, as intended. [fitting.py:3317](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3317)

   **MAJOR — an impossible recheck can still become STALE.** The API normalizes the request before reaching the new numerics-aware handler and returns unconditional `mismatch/request` on failure. I reproduced this with a valid seal using `endpoint_avg=3`, then simulated newer numerics accepting only 1–2: the API returned `mismatch`, although this server could no longer recheck the older request. Apply the numerics-aware classification to this boundary too. [app.py:1411](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1411)

   **MINOR — malformed software records are not consistently schema mismatches.** Only the six identity fields are validated. I obtained `consistent` with `git_dirty="broken"`, an object-valued commit, and all three informational fields missing. Information-only should mean values do not gate confirmation, not that their schema is unchecked. [fitting.py:3318](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3318)

2. **Numerics identity: relevant fields, but not a complete numerical execution identity.**

   **MAJOR — equal version strings do not establish equal numerical implementations.** The identity omits architecture and numerical-library build/backend information. The repository itself documents different BLAS implementations and platform-sensitive numbers. Such deployments can share all six keys, so a runtime-induced difference can be classified as `mismatch` rather than `unconfirmed`. Independently versioned `asteval`, used to evaluate linked parameters, is another omitted dependency. [fitting.py:56](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:56), [autofit-gates.yml:12](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/.github/workflows/autofit-gates.yml:12), [parameter.py:1002](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py:1002)

   I found no clearly irrelevant included field. `seed_derivation` overlaps with the application numerics version but can affect the request-derived seed.

   For an actual arithmetic difference, **other numerics → unconfirmed is sound and conservative**; same numerics → mismatch is appropriate where deterministic evaluation is established. However, the blanket `_Mismatch` handler also converts schema failures into “the recomputation differs.” I reproduced that with a string-valued statistic under another numerics version. Structural invalidity should be distinguished from numerical incompatibility. [fitting.py:3332](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3332)

3. **Digest: neither complete nor restricted to fitting math.**

   **MAJOR — a number-changing dependency escapes.** Only `_normalise_fit_request` is included from `app.py`, although it calls `_parse_int` to select background endpoints. Changing `_parse_int` to shift a supplied index by one left the digest unchanged; an in-memory verification then failed on the changed background. Include the numerical dependency closure, not just the caller. [numerics_digest.py:70](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:70), [app.py:89](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:89), [app.py:1523](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1523)

   **MAJOR — non-math changes force a bump.** Editing only the debug message “refinement outside the search box raised” changes the digest. Logging calls, error wording, and equivalent refactors inside included functions all count. That contradicts “bumped only by changes to fitting math.” [numerics_digest.py:63](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:63), [fitting.py:1848](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:1848)

   Existing module-level numerical constants and dispatch tables are included. I found no currently excluded helper used to calculate fitted numbers; verifier arithmetic is deliberately excluded.

   **MINOR — history enforcement assumes append-only maintenance.** The tests detect an unchanged manifest, duplicate versions, and adjacent equal digests. They do not protect existing entries: replacing the current entry’s digest without bumping its version passes. The append helper prevents that workflow, but the tests do not enforce it. [test_numerics_version.py:18](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:18)

4. **Tests: the deployment regression is effective; some digest claims are untested.**

   The deployment test correctly replaces the **server’s** `SOFTWARE`, preserves the sealed record, and asserts matching numerics. I ran its assertions successfully, then restored the old whole-software gate in memory: **the test failed as intended**. The other new server cases also passed with an in-memory seal. [test_seal_1a_verify.py:225](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_seal_1a_verify.py:225)

   The browser additions exercise real verification and verdict mapping, but mutate the saved identity rather than exercise an existing cache across deployment. [test_browser_seal_step4.py:543](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:543)

   **MINOR — the docstring regression test is ineffective.** It edits `verify_fit`, which is excluded entirely. Disabling docstring stripping still lets the test pass. The statistics “math” mutation is also merely `n_varys = n_varys`, and these mutation assertions use a duplicate digest helper rather than `math_digest`. Test an included function’s docstring and real arithmetic through the production digest. [test_numerics_version.py:37](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:37)

5. **Page, caches, and 1b.**

   **MAJOR — the existing cache does not implement “changed numerics triggers the recheck.”** Verdicts are keyed only by seal object; `_ensureVerified` skips any cached answer without inspecting verifier identity. An open page can retain an old commit-only `unconfirmed`, or retain `current` after server numerics change. Reloading discards the WeakMap, and explicit retry works, but automatic invalidation is absent. This is pre-existing behavior left unresolved by the new rule. [index.html:9056](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9056), [index.html:9163](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9163)

   Fresh verdict mapping remains correct: `consistent → current`, `mismatch → stale`, otherwise `unconfirmed` with its reason. [index.html:9197](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9197)

   I confirmed the covered fitting-math AST is identical to `seal-1c-page`; this diff does not change fitted numbers. The LA exception remains intact. The logged **64/1,312** result was not independently revalidated: the referenced 1b findings directory is absent from this checkout. [fitting.py:3148](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3148), [PROGRESS.md:48](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/docs/autofit/PROGRESS.md:48)

Validation was read-only: three numerics tests passed, new server assertions and targeted mutations ran in memory. The browser suite was not run.

**VERDICT: NO-GO.**
