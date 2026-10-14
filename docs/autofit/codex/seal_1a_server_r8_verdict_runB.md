Reviewed **HEAD `a220f82`**, excluding concurrent working-tree edits. All line references below refer to that commit. No files changed.

**MAJOR — a finite start producing NaN bypasses verification.**

[fitting.py:3362](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3362) evaluates the starting model but discards its result; only exceptions cause rejection. Gaussian evaluation can return NaN without raising. With a caller seed, the seed check also does not bind the starting values ([fitting.py:3403](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3403)), which are subsequently replaced by O’s fitted values.

Reproduced through the routes, using in-memory session storage:

- Data: `x = np.linspace(-5, 5, 101)`, `y = 10 + 100*np.exp(-x*x)`.
- One Gaussian: `center=0`, `amplitude=100`, `fwhm=1.5`, `fwhm_min=0`, `fwhm_max=15`.
- Background `none`, method `leastsq`, `n_perturb=0`, caller `seed=123`.
- Fit returns HTTP 200; its response verifies `consistent`.
- Change **only R’s starting `fwhm` to `0`**, retaining O.
- Verification still returns **`consistent`**.
- Fitting that changed request returns **HTTP 422**: “The array returned by a function changed size between calls.”

At zero width, the starting Gaussian contains NaN at its center ([fitting.py:118](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:118)). Every saved input number is finite. This is a request the producer refuses, not an altered convergence assertion.

Answers to the five questions:

1. **False stale:** none found. All 127 existing verification cases passed against the pinned code, including all five methods, seven shapes, backgrounds, links, holds, bounds, scattered starts, required-component checks and caller seeds ([tests:62](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/tests/test_seal_1a_verify.py:62)).

2. **False consistent:** **yes**, the MAJOR reproduction above. The current regression covers an evaluation that *raises*, missing evaluation that returns NaN ([tests:588](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/tests/test_seal_1a_verify.py:588)).

3. **HTTP 500:** no input-triggered example found. Internal verification exceptions become `unconfirmed` ([fitting.py:3304](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3304)); the route still retains an outer HTTP 500 fallback ([app.py:1421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1421)).

4. **Documentation:** the plan’s claim that refused starts receive `mismatch / request` is too broad given this reproduction ([plan:150](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/superpowers/plans/2026-10-13-seal-1a-server.md:150)). The README and API table correctly describe Q7’s evaluation-only exception and acceptance “as recorded” ([README:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/README.md:49), [CLAUDE.md:58](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/CLAUDE.md:58)). **MINOR:** [suites.md:11](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/suites.md:11) still labels 123 tests “at HEAD”; HEAD has 127.

5. **Tolerance / second reading:** no verification tolerance or divergent numerical conversion found. Comparisons remain exact and typed ([fitting.py:3156](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3156)). The statistics floor is reproduced identically, not used as a comparison tolerance ([fitting.py:2997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2997)). The finding is incomplete starting-model validation.

Validation used all 127 parameterized test cases with an in-memory session adapter. Full pytest and JS suites were reviewed as historical results, not rerun.

**VERDICT: NO-GO.**
