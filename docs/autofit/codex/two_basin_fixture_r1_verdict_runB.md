# Two-basin fixture — Codex round 1, run B (commit a1bfa0f)

One **MAJOR** finding: the documented selection measurement does not reproduce.

The [plan, line 48](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:48) and [generator docstring, line 19](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/scripts/two_basin_fixture_search.py:19) claim the selected fixture has the **largest chi2 gap among robust candidates**. The committed generator’s functions produce:

| Candidate `(amplitude, start, noise seed)` | Student χ²ᵣ | Alternative χ²ᵣ | Gap |
|---|---:|---:|---:|
| `(0, 285.2, 5)` | 39.864248 | 1.661332 | **38.202916** |
| `(700, 285.2, 1)` | 41.597748 | 8.255616 | **33.342132** |
| Selected `(1400, 285.2, 2)` | 46.931123 | 13.663083 | **33.268040** |

All three qualify and pass every committed robustness check. I confirmed these results in a fresh process. Both counterexamples also have same-fit, alternative and not-better starts. Correct the selection rationale to the actual criterion, or make the selection follow the claimed criterion. This is MAJOR under your measurement-discrepancy rule.

The remaining checks were favorable:

- **Generator totals reproduced:** 75 candidates, 15 qualifying, 7 robust.
- **Fixture outcome reproduced:** certified without movement; four alternative starts, one same, one not better.
- **260 additional probes passed** whole-fit equality: count and endpoint changes, energy ulps, individual start changes, combined random perturbations and allocation shifts. No basin change found.
- **Tests:** 70 passed across the affected modules; 112 passed with reproducibility tests first and the affected modules reordered. Six excluded API cases passed separately using memory-backed storage. Full-precision CSV parsing and the fit route matched the direct response.
- **Coverage remains active:** alternatives exist, the not-better conditional executes, and the broad-component case rejects missing shape identification. No active legacy-line or v1-seed pin remains; old measurements persist in historical findings.
- **Continuation:** one LM call capped at six evaluations, followed by two uncapped Trust-Region calls; movement **1.939813 eV**. Sixty rounding variants passed. The wrapper would cap additional LM scattered/refit calls, but this request makes none.

**MINOR:** §2 overstates the mathematical argument: multiple minima do not guarantee a randomly perturbed restart lies near a boundary. Using `n_perturb=0` preserves these tests’ stated machinery checks, while narrowing their reproducibility coverage to that request. Also, the documented objective tolerance is `3e-7`; the comparator uses `1e-7`.

Review remained read-only.

VERDICT: NO-GO.
