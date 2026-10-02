# Background math implementation round 12 — run B (commit b3fce06; codex exec, reasoning high)

Reviewed `b3fce06`, read-only.

1. **MAJOR — Tougaard still certifies, saves and restores a finite curve that violates its defining sum.** [fitting.py:817](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:817), [certificate:992](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:992), [page:4620](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4620).

   Use Tougaard, averaging 1, full window:

   ```text
   E = [0, 1, 9.999999999999999e79, 1e80]
   I = [0, 1e200, 1e145, 1e200]
   ```

   Both sides return **`[0,0,0,1e200]`**, certified. Independent Fraction evaluation of the stated discrete sum gives **`[0,0,9.999999561638153e199,1e200]`**—an error of **99.999996% of the intensity span**.

   `u*u` overflows, turning nonzero kernel terms into finite zeros. The certificate recomputes those same corrupted sums and accepts because the high-edge sum remains nonzero. Final-value finiteness cannot detect this.

   Reproduced `/api/background` returning **HTTP 200**, the production page producer returning `converged:true`, `_doSaveSpectrum` saving the incorrect background without a failure, and restoration accepting it.

   There is also cancellation in the final anchoring expression at [fitting.py:936](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:936) and [page:4637](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4637): `E=[280,285,290]`, `I=[1e20,2e20,50]` produces **16384 at the high-energy endpoint instead of its required 50**, certified in both grid directions. Guarding kernel overflow alone would leave this case. Evaluate reliably or refuse when the defining relation cannot be satisfied.

The `_legacy_line` pin is disclosed honestly, but it does mask changed fixture outcomes. After reading every test in the three modules, I ran them with the pin disabled: **66 passed; these three failed and then passed with the pin restored**:

- [test_fit_equality.py:247](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_fit_equality.py:247): `test_an_alternatives_centres_are_scaled_by_its_own_widths`—the required alternative was absent.
- [test_fit_equality.py:391](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_fit_equality.py:391): `test_an_alternative_whose_curve_cannot_be_reconstructed_fails_closed`—the expected reconstruction failure was not exercised.
- [test_runfit_certificate.py:207](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_runfit_certificate.py:207): `test_a_continuation_that_relocates_a_component_by_more_than_1_ev_is_reported`—the largest movement was **0.00129 eV**.

These support the documented basin-sensitivity explanation, not a new background-validity defect. I would retain the owner-accepted stopgap and its logged follow-up. Six upload-dependent tests were blocked by filesystem restrictions; the unpinned results are one run, not a guarantee against flakiness.

The exact-line fix passed **1,802 additional cases**, including descending grids, extrapolation, signed zeros and overflow refusals, with no page/server mismatch. At 4,000 points, evaluation took approximately **22 ms page / 29 ms server**.

Verification also covered **76 Python background tests, 64 JS checks, and 144 valid/corrupted loader cases** across both formats and orders. All four measurement summaries, the **3/62/56 census**, **376 Smart comparisons**, and **2,424 upload-rounding cases** reproduced. Full browser suites were not rerun. The two dispositioned pre-existing issues remain dispositioned. No files changed.

**VERDICT: NO-GO.**
