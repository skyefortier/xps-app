# Background math implementation round 7 — run A (commit 11733d8; codex exec, reasoning high)

Reviewed `11733d8`, read-only.

1. **MAJOR — Rounding collisions make stacks subtract from the wrong sample.** [templates/index.html:9623](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9623).
   Load `E=[0.99996,1,2,3,4,5,6]`, counts `[900,10,40,35,25,22,20]`, ROI `[1,6]`, linear background. The valid fit restores, but alignment matches the excluded `0.99996` sample to fitted energy `1` before reaching its exact match. The stack displays net intensity **890 instead of 0** there. Reproduced through the spectrum loader and stack dataset builder; server fitting succeeds. Alignment must preserve the selected sample indices.

2. **MAJOR — Manual fallback certifies and saves zeros for a one-point ROI.** [templates/index.html:4883](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4883), [zero-return branch:4555](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4555).
   Load `E=[2,1,0]`, counts `[30,20,10]`, select ROI `[0.9,1.1]`, and choose Manual with no anchors. The fallback returns `[0]`, marked converged, although it does not pass through the selected endpoint `(1,20)`. Executing `_doSaveSpectrum` writes **background `[0]`, residual `[20]`, and no failure**. The server’s manual fallback returns background `[20]` and net `[0]`. The page must produce the endpoint value or report failure.

3. **MINOR — `_pyG3` differs from Python at rounding ties.** [templates/index.html:4679](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4679).
   Certifying `E=[0,1,2]`, `I=[0,100,0]`, candidate background `[0,12.25,0]` reports **12.3%** on the page versus **12.2%** on the server. JavaScript’s tie rounding differs from Python’s. Both reject; this affects diagnostic formatting only.

Verification: **71 Python and 61 JS checks passed**, plus **216 grid-pathology parity cases**. All four measurement summaries and the **3/62/56 restore census** reproduced exactly; 242 committed Smart comparisons were bit-identical. HTTP/browser suites were not rerun under read-only restrictions; lifecycle reproductions executed extracted production functions in memory. No files changed.

**VERDICT: NO-GO.**
