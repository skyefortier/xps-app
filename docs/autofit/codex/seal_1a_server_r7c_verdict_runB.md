Reviewed HEAD `5340264`. **One MAJOR finding.** No files changed.

**MAJOR — an unevaluable finite starting value can verify `consistent`.**

Reproduced through both routes:

- Fit a Lorentzian with `center: 285`, `amplitude: 280`, `fwhm: 1`, `fwhm_min: null`, `fwhm_max: null`, background `none`, `n_perturb: 0`, and caller `seed: 12345`.
- Use 101 energies from 280–290 and counts `20 + lorentzian(x, 300, 285, 1)`.
- Keep the returned O unchanged; change only R’s starting `fwhm` to finite `1e160`.

For **leastsq, least_squares, and nelder**, the modified request returns **HTTP 422 from `/api/fit`**, but its pairing with the original O returns **`consistent`**.

The caller-seed branch checks only the supplied seed ([fitting.py:3392](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3392)). The verifier then overwrites the free starting value with O’s fitted value before evaluating ([fitting.py:3458](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3458)). The producer’s initial Lorentzian evaluation instead overflows at `hwhm ** 2` ([fitting.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:124)). This failure precedes optimisation; it is not an “as recorded” convergence question.

Validate the producer-required initial evaluation before replacing starting values, using the same effective parameters and without running the optimiser.

Answers to the five questions:

1. **False stale:** none found. The focused suite covers all five methods, seven shapes, backgrounds, links, holds, bounds, starts, required checks and caller seeds ([tests:62](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/tests/test_seal_1a_verify.py:62)). All 22 additional successful fits across the five methods verified consistently.
2. **False consistent:** yes—the MAJOR finding above.
3. **HTTP 500:** no input-triggered example found, including 286 malformed request/response probes. Internal verifier exceptions become `unconfirmed` ([fitting.py:3302](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3302)); the route retains its final 500 fallback ([app.py:1417](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1417)).
4. **Docs:** the plan, README and CLAUDE API table now correctly limit Q7 to evaluation identities. **MINOR wording:** the function docstring still broadly says “a curve-derived check” ([fitting.py:3277](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3277)); align it with the corrected descriptions.
5. **Tolerance/second reading:** no new comparison tolerance or divergent numerical conversion found. The statistics floor is reproduced identically, not used as a verification tolerance ([fitting.py:2997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2997)). The finding is omitted initial-evaluation validation.

Validation: **123 focused tests passed**, using in-memory session storage for read-only operation. The recorded full Python and JS results remain at their stated commits ([suites.md:3](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/suites.md:3)); neither was rerun.

**VERDICT: NO-GO.**
