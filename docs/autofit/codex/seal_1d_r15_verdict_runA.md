**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Yes, the round-14 findings are resolved.** Identifier normalization is checked before fitting and during response validation; value-equal response IDs are rejected; expression names use Python’s tokenizer; fixed bounds include held-value widening. See [fitting.py:1771](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1771), [fitting.py:271](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:271), [same_fit.py:122](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:122), and [fitting.py:332](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:332). I independently confirmed that all five reported mutants are caught.

2. **No, validation still accepts structures the producer cannot write.**

   **MINOR — impossible bounds remain accepted outside `_FIXED_BOUNDS`.** Starting from a real response, change `individual_peaks[0].params.fwhm` to either `min:15, max:0.1` or `min:1, max:1`. Both pass validation and return **200 on a, b, and both**, with self-comparison reporting **`same:true`**. Actual `run_fit` swaps the reversed bounds and refuses equal bounds. The validator checks these spans only for overflow at [fitting.py:378](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:378); lmfit enforces ordering and unequal bounds at [parameter.py:886](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py:886). A lone infinite bound with the other bound null also passes, although the producer serializes nonfinite bounds as null at [fitting.py:3222](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3222).

   **MINOR — impossible metadata values remain accepted.** Setting `fit_method:"not-a-method"` or `seed_source:"impossible"` passes validation and self-compares with **200**. Validation checks only string types at [fitting.py:176](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:176). The producer restricts methods at [fitting.py:2749](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2749) and writes only `"caller"` or `"request"` at [fitting.py:3314](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3314).

   I found no new rejection of producer output. The documented exception remains: a successful fit with held FWHM bounds `[-1e308,1e308]` fails validation at that parameter’s `min/max`. I reproduced it; it is explicitly acknowledged in [plan:114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:114).

3. **I did not reproduce a body-triggered 500.** The 3,000-mutation fuzz and additional malformed JSON, excessive-nesting, and oversized-integer probes passed. This does not prove “never”: unexpected comparison exceptions still return 500 at [app.py:1486](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1486).

4. **The tests establish the specific regressions, but the bounds-coverage claim is overstated.**

   **MINOR — the shape matrix misses linked components with independent shape parameters.** Every linked matrix case sets `fix_fwhm=True`; its lock flag changes only the master’s centre and width. See [tests/test_seal_1d_compare.py:424](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:424). I changed the linked DS `gamma_asym` and DS+G `m_gauss` fixed upper bounds to **99** in memory: **all 28 matrix tests still passed**. Those branches need real-fit controls with `fix_fwhm=False`.

Read-only verification using in-memory sessions: **290 passed, 2 skipped, 5 chain-related tests deselected**. Separately, all **328 archived records** validated and self-compared successfully; their hash matches the manifest. Browser tests and the complete 605-test suite were not rerun. No files changed.

VERDICT: NO-GO
