**One MINOR remains. No BLOCKER or MAJOR found.**

1. **Round-7 finding: resolved.** Whole-text matching rejects comments and trailing operators. Accepted expressions expose exactly one resolvable master to both validation and the comparator’s regex. [app.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1454), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

2. **MINOR — duplicate IDs in scattered-start alternatives make position scales ambiguous.**  
   Path: `starts.alternatives[i].components[j].id`.

   The endpoint checks uniqueness only in `individual_peaks`. However, `alternative_widths` also indexes widths by component ID, allowing a later duplicate to overwrite an earlier component’s scale. [app.py:1479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1479), [same_fit.py:233](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:233)

   **Reproduced:** two alternative components share an ID, with reconstructed widths approximately **0.1** and **9.8**. Changing the first component’s `center_shift_from_start` from **0 to 0.001** returns **200, `starts.same: true`** because it receives the wider component’s tolerance. Giving the second component its distinct ID makes the same change return **`starts.same: false`**. [same_fit.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:193)

   Duplicate alternative IDs placed only in **a**, only in **b**, or in both are compared rather than refused. Validate uniqueness within each alternative on both sides and add regression coverage. I reproduced no additional non-finite-scale acceptance or HTTP 500.

3. **Real-fit compatibility: no new refusal found.** All **328 stored records**, the five offset cases, and **14 additional real fits** across all seven lineshapes with linked widths locked/unlocked and exponent-form offsets/ratios self-compared `same`. The producer’s expressions match the grammar. [fitting.py:1730](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1730), [tests/test_seal_1d_compare.py:206](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:206)

   The documented refusal of otherwise successful fits with bounds ±1e308 remains. [plan:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:69)

4. **New tests detect their named defects.** In-memory mutations confirmed that prefix matching fails **seven cases**, while restoring the previous AST rule fails **both comment cases and the subtraction case**. They do not cover duplicate alternative IDs. [tests/test_seal_1d_compare.py:272](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:272)

Validation: **90 tests passed, zero skipped**. Tests used in-memory session storage; no checkout files changed.

VERDICT: NO-GO
