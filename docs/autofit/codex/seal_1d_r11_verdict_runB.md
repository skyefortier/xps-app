**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Round-10 findings: the specific counterexamples are fixed, but the broader compatibility and oracle claims remain incomplete.** The hostile cases now have assertions for a, b, and both; the listed IDs and expanded real-fit variants pass. [tests/test_seal_1d_compare.py:221](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:221), [tests/test_seal_1d_compare.py:402](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:402)

2. **No: the validator still rejects real responses and accepts structures the producer cannot write.**

   **MINOR — valid integer IDs are rejected.** With `individual_peaks[0].id = 9007199254740993`, `/api/fit` returns **200, `success: true`**. Its unmodified response self-compares with **400**. The producer echoes the ID unchanged, but `_representable` applies float exactness to every integer—including identifiers. I also reproduced this with ID `10**400`. [fitting.py:232](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:232), [fitting.py:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:247), [fitting.py:3155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3155)

   **MINOR — link validation remains broader than the producer.** Two confirmed examples:
   
   - `individual_peaks[1].params.center.expr = "p1_center + -0.0"` passes. The producer explicitly folds negative zero to positive zero before writing the expression.
   - An isolated `params.fwhm` link, with `center.expr` and `amplitude.expr` both null, passes. The producer always creates centre and amplitude links when linking a component.

   Each example returns **200 on a, b, and both**, and self-comparison reports **`same: true`**. The validator checks expressions independently; it does not enforce the producer’s complete link arrangement. [fitting.py:216](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:216), [fitting.py:272](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:272), [fitting.py:1851](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1851)

3. **I did not reproduce a body-triggered 500.** The fuzz passed, and additional malformed JSON, deeply nested JSON, and oversized-integer bodies returned 400. That does not prove the universal “any body” claim; an unexpected comparison exception still explicitly returns 500. [app.py:1480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1480)

4. **The tests support their bounded regression results, but the oracle overclaims.**

   **MINOR — required-key deletions are skipped.** `OPTIONAL_KEYS` is applied by key name globally, so the oracle never deletes required top-level `message` or `background_verdict.reason`. I verified this with an in-memory mutant accepting both omissions: **the oracle still passed**, while those malformed responses self-compared with 200. Optionality must depend on the object’s path/schema. [tests/test_seal_1d_compare.py:359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:359), [tests/test_seal_1d_compare.py:381](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:381)

   Read-only execution with in-memory upload fixtures produced **174 passed, 2 skipped** for comparison/digest tests; comparator tests also passed. Independently, **all 328 original records passed and self-compared `same`**, with the corpus hash matching its manifest. I did not rerun the full reported 394-test set.

No checkout files changed.

**VERDICT: NO-GO**
