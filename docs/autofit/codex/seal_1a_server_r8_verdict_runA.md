Reviewed HEAD `a220f82`. **One MAJOR finding; no BLOCKER found.** No files changed.

**MAJOR — a non-finite starting evaluation still permits false `consistent`.**

The new start check discards the evaluation’s return value and catches only exceptions ([fitting.py:3362](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3362)). A finite request can produce an entirely infinite curve without raising.

Reproduced through the routes:

- Energies: `np.linspace(280, 290, 101)`.
- Counts: `20 + 300 / (1 + ((x - 285) / 0.5)**2)`.
- One Lorentzian: `center: 285`, `amplitude: 280`, `fwhm: 4`, `amplitude_min: null`, `amplitude_max: null`.
- Background `none`, `n_perturb: 0`, caller `seed: 12345`.
- Save the successful response O, then change **only R’s starting amplitude to `1e308`**.

For both **leastsq and nelder**, the modified request returns **HTTP 422 from `/api/fit`**, but verification against unchanged O returns **`consistent`**.

The Lorentzian calculation produces 101 infinities ([fitting.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:124)). With non-finite residuals omitted, leastsq fails immediately with `N=3 … M=0`; nelder rejects the objective. Verification instead replaces the starting amplitude with O’s finite fitted value ([fitting.py:3473](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3473)).

The start check must inspect the evaluated values and handle an unjudgeable initial evaluation before replacing parameters. No tolerance or optimiser rerun is needed.

Answers to the five questions:

1. **False stale:** none found. The passing verifier tests cover all five methods, seven shapes, backgrounds, links, holds, bounds, scattered starts, required checks and caller seeds ([tests:62](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/tests/test_seal_1a_verify.py:62)).

2. **False consistent:** yes—the MAJOR finding above. The failure occurs at the initial objective, independently of the recorded convergence assertions.

3. **HTTP 500:** no input-triggered example found, including **650 malformed/type/value probes**. Internal verifier exceptions return `unconfirmed` ([fitting.py:3304](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3304)); the route retains a final 500 fallback ([app.py:1421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1421)).

4. **Docs:** Q7’s scope and the “as recorded” exclusions are correctly described in the [README:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/README.md:53) and [CLAUDE.md:58](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/CLAUDE.md:58). The [plan’s start-refusal guarantee:150](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/superpowers/plans/2026-10-13-seal-1a-server.md:150) remains incomplete because of this finding. **MINOR:** [suites.md:11](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/suites.md:11) still labels 123 verifier tests as HEAD; HEAD has 127.

5. **Tolerance / second reading:** no verification tolerance or divergent numerical conversion found. The existing statistics floor is reproduced identically, not used as an equality tolerance ([fitting.py:2999](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2999)). The finding is omitted validation of the initial evaluation’s result.

Validation: **149 passed**, including all **127 verifier tests**, using in-memory sessions. Four filesystem-writing provenance tests were excluded. Full pytest and JS results were reviewed at their recorded commits, not rerun.

**VERDICT: NO-GO.**
