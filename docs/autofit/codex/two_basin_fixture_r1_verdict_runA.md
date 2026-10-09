# Two-basin fixture — Codex round 1, run A (commit a1bfa0f)

No BLOCKER or MAJOR found on `853fed6..a1bfa0f`. The fixture and restored tests survived the adversarial checks.

- Reproduced **75 candidates, 15 qualify, 7 robust**.
- Reproduced the chosen fixture: χ²ᵣ **46.931123**, certified without movement; **4** starts reach **13.663083**, **1** matches, **1** is not better.
- **226 additional probes passed** whole-response comparison: count ulps, endpoint levels, energy ulps, starting-parameter changes, and allocation/alignment changes.
- Full-precision CSV preserved both arrays exactly; the API response matched the direct fit. Disk storage was replaced with in-memory storage for this read-only review.
- **112 Python tests passed** with reproducibility tests first; **70 passed** with the changed modules reversed. API fixture test passed separately; **32 relevant JavaScript tests passed**.
- No vacuous alternative-dependent test found. The broad-component case produced three alternatives and correctly failed when explicit shapes were removed. The conditional not-better assertions still execute.
- The deliberate continuation moved **−1.939813 eV** in two uncapped Trust-Region restarts. Only the initial LM call received the six-evaluation cap; 24 additional continuation probes passed. The wrapper would cap other LM calls, but this request makes no scattered-start or required-component refit calls.
- Both legacy pins are removed.

Remaining findings are **MINOR wording**:

1. **Define “largest chi2 gap.”** The [generator description](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/scripts/two_basin_fixture_search.py:19) and [plan](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:48) omit the comparison target. Gaps to the *best* alternative are:

   | Robust candidate `(amplitude, start, seed)` | Gap |
   |---|---:|
   | `(0, 285.2, 5)` | 38.202916 |
   | `(700, 285.2, 1)` | 33.342132 |
   | Chosen `(1400, 285.2, 2)` | 33.268040 |

   The chosen fixture instead wins on gap to the **worst listed alternative**. Specify that metric if intended.

2. **The restart argument overstates necessity.** [Plan §2](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:23) should say perturbed restarts *can* approach boundaries. Multiple minima do not guarantee that. Using `n_perturb=0` is defensible for these tests; it narrows their coverage, while other tests retain perturbed-restart coverage.

3. **Correct two stale statements.** The [plan’s objective tolerance](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:41) is **1e-7**, not 3e-7. The [certificate findings document](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/docs/findings/runfit-certificate/README.md:175) should identify the χ²ᵣ ~286 two-basin example as historical.

VERDICT: GO
