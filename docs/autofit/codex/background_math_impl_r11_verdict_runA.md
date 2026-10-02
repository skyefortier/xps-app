# Background math implementation round 11 — run A (commit 60025c7; codex exec, reasoning high)

1. **MAJOR — Linear still certifies, fits against, and saves a finite curve that misses its defining line.** [fitting.py:579](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:579), [templates/index.html:4928](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4928).

   Load this finite, descending dataset and select Linear with the full background window:

   ```text
   E = [1e20, 290,289,288,287,286,285,284,283,282,281,280]
   I = [1e20,  70, 70, 80,120,500,120, 80, 70, 70, 60, 50]
   ```

   The correctly rounded line through its endpoints is `[1e20,60,59,…,50]`. Both implementations instead return `[1e20,0,0,…,0]`: subtraction loses the offsets, then cancellation produces zero. Every intermediate remains finite, so the guards accept it.

   I reproduced `converged:true`, successful `run_fit`, and the actual `_doSaveSpectrum` function writing those zeros with `backgroundFailure:null`. This violates owner item 2. Linear—and manual’s fewer-than-two-anchor fallback—needs accurate affine evaluation or explicit refusal.

The round-10 manual fix passed **10,006 exact-double checks**, **12,890 rational-rounding checks**, and **44,871 bit-identical page/server values**. Performance for 4,000 points × 12 anchors: approximately **29 ms page / 67 ms server**.

Verification: **75 Python and 63 JavaScript tests passed** using read-only wrappers; **64 valid and 64 corrupted loader cases** covered all eight methods, both formats and both orders. All four measurement summaries, the **3/62/56 census**, **376 Smart comparisons**, and **2,424 upload-rounding measurements** reproduced. The two dispositioned issues remain dispositioned. Full browser/HTTP suites were not rerun. No files changed.

**VERDICT: NO-GO.**
