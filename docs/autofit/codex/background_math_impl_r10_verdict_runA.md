# Background math implementation round 10 — run A (commit ad80814; codex exec, reasoning high)

Reviewed `ad80814`, read-only.

1. **MAJOR — Manual interpolation still certifies an incorrect finite curve.** [fitting.py:626](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:626), [templates/index.html:15085](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:15085).

   Use energies `280..290`, counts `[80,81,92,133,484,135,96,87,88,89,90]`, and manual anchors `(-1e20,-1e20)` and `(300,100)`. Their affine background is **80..90 counts**, confirmed with high-precision arithmetic. Both implementations instead return **all zeros**: subtraction loses the small offsets, then cancellation erases the result. Every intermediate remains finite, so round 9’s checks pass.

   Reproduced page `converged:true`, a spectrum save containing zeros with `backgroundFailure:null`, and `/api/fit` returning **HTTP 200, `success:true`** against that background. This violates item 2. Check the affine relation or refuse numerically unreliable interpolation; finiteness alone is insufficient.

Verification: **84 Python and 63 JS tests passed**, plus **96 loader round trips**, **900 numerical parity probes**, and **376 bit-identical Smart comparisons**. All four measurement summaries and the **3/62/56 census** reproduced exactly. Upload-rounding results reproduced: maximum **8.59e-7**, matching verdicts across **2,424 cases**. The two dispositioned pre-existing issues are not re-raised. Full browser suites were not rerun; lifecycle probes used extracted production functions. No files changed.

**VERDICT: NO-GO.**
