The fresh verifier implements the central recomputation rule, but the version guard and existing page caches prevent an exact implementation. **Three MAJOR findings; no BLOCKER found.**

1. **Owner’s rule: correct for a fresh verification, incomplete end to end.**

   Commit, checkout state and environment digest no longer gate confirmation. `consistent` is returned only after `_verify` completes; failed required recomputations do not become `consistent`. Acceptance remains recorded, as required. See [fitting.py:3313](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3313).

   **MAJOR — cached verdicts bypass the new rule.** An open page can retain an old `unconfirmed/software` verdict caused solely by a commit difference. It can also retain `consistent` across a numerics deployment without rechecking. Background triggers return immediately whenever a verdict exists; its recorded software is never compared. I reproduced both cases using the actual JavaScript: zero verification requests; explicit retry issued one. Reload/manual retry recovers. See [index.html:9163](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9163).

   **MINOR — malformed software validation is incomplete.** Only the six numerics fields are checked. A record with `git_commit: 123`, `git_dirty: []`, and `env_sha256: {}` still verifies `consistent`; so does one containing only the six keys. That falls short of “malformed software is a schema mismatch.” See [fitting.py:3318](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3318).

2. **Numerics identity and verdict classification: reasonable policy, incomplete identity.**

   All six fields can affect fitting numbers; none is clearly irrelevant. However, version strings do not identify numerical builds/runtime completely: architecture, BLAS/libm implementations and transitive expression-evaluation dependencies are omitted. The identity records package versions only ([fitting.py:106](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:106)); fitting also evaluates linked expressions ([fitting.py:1628](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:1628)). **MINOR — treat this as a declared compatibility identity, not proof of identical arithmetic.** Cross-platform equivalence was not established by 1b.

   A differing recomputation under other numerics reading `unconfirmed` is conservative and sound: it does not falsely confirm anything. It does not prove the numerics change caused the difference. The blanket conversion also includes schema/request failures, so deliberately sacrifices some definite mismatch diagnoses. Under genuinely identical, deterministic numerics, `mismatch` remains appropriate; LA’s existing evaluation exception remains intact. See [fitting.py:3330](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3330).

3. **Digest: does not capture exactly “changes to fitting math.”**

   **MAJOR — numerical changes escape through dependencies outside the selected AST.** The digest selects only `_normalise_fit_request` from `app.py`, omitting its `_parse_int` dependency ([numerics_digest.py:70](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:70), [app.py:89](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:89), [app.py:1523](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1523)).

   In memory, changing `_parse_int`’s returned index by one:
   - Left the digest unchanged.
   - Changed background indices `(10,120)` to `(11,121)`.
   - Moved the background by up to **22.6055 counts**.
   - Made the original seal report **`mismatch/background` under the unchanged numerics version**.

   Excluded verifier functions also contain arithmetic: changing verification weights at [fitting.py:3435](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3435) leaves the digest unchanged. Excluding verifier edits is intentional, but therefore this digest cannot promise to track every change to a *recomputed* number. Shared numerical operations should live in the covered math.

   **MAJOR — non-math changes force bumps.** Changing only `"Circular peak constraint detected:"` changes the digest. No fitted number changes, yet the version test demands a bump. Error messages, logging and equivalent refactors inside included functions have the same problem. See [fitting.py:1549](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:1549) and [test_numerics_version.py:24](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:24).

   Ordinary module-level constants are covered. The history tests correctly enforce current-pair agreement, unique versions and different adjacent digests **assuming prior entries remain unchanged**; they do not independently establish historical append-only behavior or semantic math equivalence. See [test_numerics_version.py:18](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:18).

4. **Tests: deployment regression test is effective; digest coverage is overstated.**

   The deployment test replaces server `SOFTWARE` while preserving the sealed record and numerics. I ran it successfully, then restored the base verifier in memory: **the test failed**, correctly detecting the old gate. See [test_seal_1a_verify.py:225](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_seal_1a_verify.py:225).

   **MINOR — the docstring test does not establish its claim.** It changes a docstring inside the already-excluded verifier, so exclusion alone makes it pass. The statistics mutation inserts `n_varys = n_varys`, demonstrating syntactic sensitivity rather than changed arithmetic. The helper also duplicates digest filtering and omits `app.py`. See [test_numerics_version.py:37](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:37).

   Browser mutations create a fresh seal, avoiding a cached verdict; they therefore exercise the new server rule but miss deployment cache invalidation. See [test_browser_seal_step4.py:20](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:20).

5. **Other regressions and 1b.**

   Fresh page responses map correctly: `consistent → current`, `mismatch → stale`, and `unconfirmed` preserves its reason. Commit information remains displayed. See [index.html:9197](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9197).

   This diff changes no fitting arithmetic or LA exception. The historical **1,248 consistent / 64 unconfirmed** observation remains valid; it is not a guaranteed count on another run. I checked the separate 1b worktree’s [README.md:43](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:43).

Validation: three numerics pytest tests passed; 13 new server cases and 44 existing mutation cases passed through the real verification endpoint using an in-memory fit fixture. Browser integration tests were inspected, not run. All mutations were in memory; checkout unchanged.

**VERDICT: NO-GO.**
