**Four MINOR findings remain. No BLOCKER or MAJOR found.**

1. **The specific round-14 findings are resolved.** NFKC-changing IDs are rejected, response IDs must be unique by value, Unicode identifiers retain their inherited bounds, and fixed shape bounds account for held-value widening. The new regression controls pass. See [fitting.py:1771](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1771), [fitting.py:273](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:273), [same_fit.py:122](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:122), and [fitting.py:337](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:337).

2. **No: the validator still accepts records the producer cannot write.**

   **MINOR — incomplete parameter-bound invariants.** Starting from a successful fit, each of these mutations passes validation and returns **200 on a, b, and both**, with self-comparison reporting **`same: true`**:
   - `individual_peaks[0].params.gl_ratio.value = 1.5`, retaining `vary: true` and bounds `[0,1]`;
   - `individual_peaks[0].params.fwhm` bounds `[15,0.1]`;
   - that FWHM’s bounds `[1,1]`.

   Validation checks fixed endpoints and span overflow, but omits value containment and bound ordering. The producer clips parameter values, sorts reversed bounds, and refuses equal bounds. See [fitting.py:337](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:337), [fitting.py:378](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:378), and [lmfit/parameter.py:886](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py:886).

   **MINOR — scattered-start IDs are checked only by spelling.** Changing `starts.fit.components[0].id` from integer `1` to string `"1"`, while retaining integer `1` in `individual_peaks`, passes validation and self-compares successfully. The producer copies the original ID unchanged. Compare [fitting.py:359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:359) with [fitting.py:2558](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2558).

   I found no new producer-response rejection. I reconfirmed the documented exception: a successful fit with held FWHM bounds `[-1e308,1e308]` returns **400**, naming that bound span. See [plan:114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:114).

3. **I did not reproduce a body-triggered 500.** The 3,000-mutation fuzz passed, and malformed JSON, excessive nesting, oversized integers, and wrong-content-type probes returned 400. This does not prove “never”: unexpected comparison exceptions still return 500 at [app.py:1486](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1486).

4. **The tests establish the specific regressions, but overstate coverage.** All five specified mutants were caught.

   **MINOR — the matrix does not protect every fixed-bound entry.** Linked children always use `fix_fwhm=True`; `lock` changes only the master’s centre and width. Changing the linked DS `gamma_asym` or linked DS+G `m_gauss` upper bound to `123` in memory left every matrix case for that shape passing. Those branches need linked children with `fix_fwhm=False`. See [tests/test_seal_1d_compare.py:424](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:424).

   **MINOR — cross-response ID types are ignored.** Two actual successful fits using the same explicit seed, differing only in component ID `1` versus `true`, return **200, `same: true`, starts same**. Python equality at [same_fit.py:294](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:294) contradicts the stated identical-ID rule at [same_fit.py:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:53).

Read-only verification: **295 passed, 2 skipped** across comparison, comparator, and numerics tests, using in-memory upload sessions. The archived 328-record corpus was unavailable; browser tests were not rerun. No files changed.

VERDICT: NO-GO
