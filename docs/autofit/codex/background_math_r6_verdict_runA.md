# Background math foundation round 6 — run A (commit 211bf7f; codex exec, reasoning high)

**Confirmed: no fitted numbers changed.** `fitting.py`’s executable AST matches `main` after removing docstrings. `templates/index.html` differs only in comments and the two Smart tooltip texts. Working tree unchanged.

No BLOCKER or MAJOR findings.

1. **MINOR — The historical round-3 table retains the superseded constraint attribution.** [README.md:344](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:344) still calls `+0.97%` the constraint’s increment and `0.30 ± 0.04 pp` its reduction.

   Concrete countercheck: seed 1, 1,000 draws, step 4000, both equations using averaged **levels**, gives **0.833410% ± 0.011411** and a paired reduction of **0.444015 ± 0.037782 pp**. The `0.972519%` production-method difference includes **0.139109 pp** from changing the reading. Annotate that historical row as superseded by round 5. Current F2 and the round-5 table are correct, so this is nonblocking.

The other round-5 repairs hold: Smart’s tooltip and the JS header require convergence; the checker correctly assigns Shirley-linear to the levels reading. The reviewed solution claims account for averaging, convergence, grid direction, near-uniform approximation and degenerate cases. F1/F2/F4/F5/F10/F11/F12 remain supported options explicitly reserved for the owner. No resemblance-based mathematical defence found.

Validation: **36 Python tests and four JavaScript tests passed**. All **121 measurement records reproduced**, with only two numerical differences below `7e-18`; the stated corpus bounds hold. The 1,000-draw Monte Carlo reproduced both step sizes and the corrected averaging comparison; residual checks passed. Full application suites were not rerun.

**VERDICT: GO.**
