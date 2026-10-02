# Background math implementation round 12 — run A (commit b3fce06; codex exec, reasoning high)

Reviewed `b3fce06`, read-only. **No BLOCKER or MAJOR finding.**

**MINOR — the legacy pin removes production-path coverage from several fixture-dependent tests.** [tests/_legacy_line.py:35](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/_legacy_line.py:35).

I read every test in the three modules and ran them with the pin removed in memory: **66 passed, 3 failed, 6 upload-dependent cases skipped**. These three failures passed when rerun with the committed pin:

| Test | Concrete production-line failure |
|---|---|
| [test_the_starts_are_a_pure_function_of_the_request — :148](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_scattered_starts.py:148) | Identical requests reached different basins: reduced χ² **2.875 versus 1.367**, with materially different component areas. |
| [test_an_alternatives_curve_is_compared_against_its_own_height — :327](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_fit_equality.py:327) | No alternative was returned; indexing `alternatives[0]` failed before testing the comparator. |
| [test_a_continuation_that_relocates_a_component_by_more_than_1_ev_is_reported — :207](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/test_runfit_certificate.py:207) | The fit certified and moved, but its largest centre movement no longer exceeded 1 eV. |

The following tests share the same dependence on repeatable basin selection or available alternatives. These are **additional susceptible assertions, not additional observed failures**:

- `tests/test_scattered_starts.py`: `test_the_fit_is_the_same_with_and_without_the_check` (:86), `test_a_lower_chi_square_solution_is_reported_beside_the_fit_not_instead_of_it` (:97), `test_starts_and_solutions_are_counted_separately` (:289).
- `tests/test_fit_equality.py`: `test_a_fit_that_lands_in_a_different_minimum_is_not_the_same_fit` (:68), `test_a_scattered_start_objective_is_compared_at_the_objective_scale` (:222), `test_an_alternatives_centres_are_scaled_by_its_own_widths` (:247), `test_an_alternative_without_a_fwhm_parameter_is_scaled_by_its_own_curve` (:281), `test_an_alternatives_bounded_parameter_uses_the_models_bounds` (:314), `test_a_lorentzian_alternative_is_not_judged_by_a_gaussian_twin` (:370), `test_an_alternative_whose_curve_cannot_be_reconstructed_fails_closed` (:391), `test_a_non_finite_reconstruction_fails_closed` (:433).

**The pin is honest as the accepted fixed-fixture stopgap.** It preserves useful tests of starts, certificates, and comparisons; it does not establish production reproducibility. The failures above demonstrate the disclosed basin sensitivity, not an incorrect background or an invalid background escaping refusal. The remaining tests retain their intended assertions; I also reproduced the API-forwarding assertion with production arithmetic and in-memory session data.

Verification:

- **76 Python and 64 JavaScript background checks passed**, including producer refusal, consumer handling, and certificate parity.
- **2,175 exact-line cases** matched page/server bits and refusal decisions, including descending grids, extrapolation, repeated endpoints, signed zeros, subnormals, and extreme magnitudes.
- **128 loader cases passed**: all eight methods, both formats and orders, exact/rounded saves, and corrupted backgrounds.
- All four measurement summaries and the **3 restored / 62 differing / 56 missing-curve census** reproduced exactly. Committed Smart parity and **2,424 upload-rounding measurements** reproduced.
- A 4,000-point exact line averaged approximately **22 ms page / 27 ms server**.
- Full browser and full-suite runs were not repeated. No files changed. The two previously dispositioned issues remain dispositioned.

**VERDICT: GO.**
