**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **The specific round-13 reproducers are fixed, but link interpretation is still inconsistent.** Duplicate-equal request IDs are rejected at [fitting.py:1778](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1778), and held expression-free shape parameters on linked components are rejected at [fitting.py:300](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:300).

   **MINOR — the Unicode regex still misses valid identifiers.** `\w` excludes combining marks and some valid identifier punctuation. Successful, verifier-consistent fits with master IDs `"a\u0305"` (`a̅`) or `"a·b"` lose their inherited bounds. Adding `0.005` to `individual_peaks[1].params.fwhm.value` returns **200, same:false**; identical controls with `"e"` and `"é"` return **same:true**. All use master bounds `[0.1, 15.0]`. The remaining mismatch is [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143).

   **MINOR — expression evaluation normalizes identifiers differently from the link walks.** With distinct IDs `"K"` and `"K"`, and a child constrained to `"K"`, I reproduced a successful fit where:
   - `"K"` has held FWHM `1.1`, bounds `[0.1,15]`;
   - `"K"` has held FWHM `2.2`, bounds `[2,2.4]`;
   - the child records `expr:"pK_fwhm"` but value **2.2**, while `support.follows` is `"K"`.

   Python’s expression parser normalizes `K` to `K`. The request lookup and support walk use literal IDs, and the comparator inherits `"K"`’s bounds. Consequently, another `0.005` child-width perturbation incorrectly compares alike against the wider bounds. Verification reports **consistent**. See [fitting.py:1893](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1893), [fitting.py:3220](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3220), [fitting.py:3884](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3884), and [same_fit.py:144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:144).

2. **No: response validation still accepts a structure the producer rejects.**

   **MINOR — response-ID uniqueness checks spelling only.** Relabeling an otherwise valid response’s components and associated ID fields to `(true,1)` or `(0,false)` passes validation. `/api/compare-fits` returns **200 on a, b, and both**, with self-comparison reporting **same:true**. `run_fit` rejects both pairs. Paths: `individual_peaks[0].id` and `individual_peaks[1].id`. Compare [fitting.py:261](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:261) with [fitting.py:1778](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1778).

   The documented producer-output exception also remains: I reproduced a successful fit with held FWHM bounds `[-1e308,1e308]` that self-compares with **400**, rejected at `individual_peaks[0].params.fwhm.min/max`. This is the stated arithmetic limitation, not an additional finding. See [fitting.py:353](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:353) and [plan:108](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:108).

3. **I did not reproduce a body-triggered 500.** The 3,000-mutation fuzz passed; additional malformed JSON, excessive nesting, oversized-integer, and wrong-content-type probes returned 400. This does not prove impossibility: unexpected comparison exceptions still explicitly return 500 at [app.py:1486](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1486).

4. **The tests establish the specific regressions, not the universal claims.** Metadata controls now check every non-area parameter’s expression, flag, and bounds on the linked component ([tests:314](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:314)). However, duplicate-equal IDs are tested only at request validation, and Unicode tolerance tests cover only `"e"` and `"é"` ([tests:552](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:552), [tests:568](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:568)). They miss all three cases above.

Read-only verification using in-memory sessions: **272 passed, 2 skipped, 5 chain-related tests deselected**. Browser tests, archived-record validation, and the mutant campaign were not rerun. No files changed.

VERDICT: NO-GO.
