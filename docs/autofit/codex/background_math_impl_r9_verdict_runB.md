# Background math implementation round 9 — run B (commit 530513f; codex exec, reasoning high)

Reviewed `530513f`, read-only.

1. **MAJOR — Manual interpolation certifies a finite but incorrect background after intermediate overflow.** [fitting.py:617](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:617), [templates/index.html:15077](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:15077).

   Load manual anchors `(-1e308, 0)` and `(1e308, 100)` with energies `280..290`. These finite anchors pass validation. Their affine background is approximately **50 counts** throughout this window. However, the anchor-energy difference overflows to infinity, making the computed slope zero. Both implementations return **all zeros**, which pass the final finiteness check.

   Reproduced through the page’s producer and spectrum saver: `converged:true`, zero background, and no failure. With counts `[50,50,60,100,500,100,60,50,50,50,50]`, `/api/fit` also returns **HTTP 200, `success:true`** against that zero background. Compared with the correct 50-count background, the Gaussian area changes from **550.24 to 703.46**, and its support verdict flips.

   This extreme but accepted input violates item 2 and changes saved and fitted numbers. Reject invalid interpolation arithmetic or verify the resulting affine relation; final-value finiteness alone is insufficient.

Verification: **82 Python and 62 JS tests passed**; two pytest fixtures were blocked by filesystem restrictions. Both empty-window API fixes passed separate in-memory checks. **192 record round-trip/frozen-stack cases**, all four measurement summaries, the **3/62/56 census**, and **376 bit-identical Smart comparisons** passed. Full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
