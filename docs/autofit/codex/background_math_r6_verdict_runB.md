# Background math foundation round 6 — run B (commit 211bf7f; codex exec, reasoning high)

**Confirmed: no fitted numbers changed.** `fitting.py`’s executable AST matches `main`; `index.html` differs only in comments and the two Smart tooltip texts. Working tree unchanged.

1. **MINOR — The retrospective retains F2’s superseded attribution.** [README.md:344](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:344), also lines 349–350.

   It still calls **+0.97%** the constraint’s increment and **0.30 pp** its averaging reduction. In the seed-1, step-4000, 1,000-draw experiment, isolating both equations on the levels reading gives **0.83341% ± 0.01141%**, with reduction **0.44402 ± 0.03778 pp**. The production-method difference includes **0.13911 pp** from F1. Annotate these historical entries as superseded by round 5. The main F2 discussion and round-5 table are correct; this is non-blocking historical wording.

No BLOCKER or MAJOR findings. The remaining round-5 fixes hold: Smart’s convergence condition, the JS header qualification, and the checker’s reading categories. The documented convergence, grid, averaging, and degenerate-window limitations cover the tested counterexamples. F1/F2/F4/F5/F10/F11/F12 recommendations follow from the evidence and explicitly remain owner decisions. No resemblance-based mathematical defence found.

Validation: **36 Python tests and 4 JavaScript tests passed**; all **121 measurement records reproduced within numerical tolerance**; the **1,000-draw Monte Carlo reproduced**, including the corrected isolated effect. Full application suites were not rerun.

**VERDICT: GO.**
