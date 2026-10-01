# Background math implementation round 9 — run A (commit 530513f; codex exec, reasoning high)

Reviewed `530513f`, read-only.

1. **MAJOR — Auto-Fit combines newly selected counts with the previous server envelope.** [templates/index.html:7542](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:7542), [result assembly:7560](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:7560).

   Reproduced with ROI `[281,291]`, constant Manual background 20, and an asymmetric graphite peak fitted near `284.53`. Final charge correction becomes `0.03`; rounding the ROI fields leaves both bounds unchanged. The selected raw window changes from `[281.02,290.92]` to `[281.12,291.02]`, retaining 100 points. The new background certifies, but `json.fitted_y` still describes the original samples. Application succeeds and reports **R = 18.57% instead of 0.0228%**. Preserve the fitted samples through correction, or refit when selection changes.

2. **MAJOR — Run Fit freezes a different background from the one the server fitted against.** [templates/index.html:8592](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:8592).

   Use Tougaard, averaging 1, `E=[0,1,2.0000005,3.0000005]`, `I=[2,3,0.008279338821039262,3]`. Upload rounding changes the inputs: the page’s background at the third point is **1001.5074**, while the server’s is **369.5577**. Both certify, and server fitting succeeds. `runFit` nevertheless pairs the page background with the server envelope. The background-subtracted Fit trace becomes **−631.9497 instead of approximately zero**; project saves retain that inconsistent pair. Reproduced through the extracted production `runFit`. The accepted result needs consistent counts, background and envelope.

3. **MINOR — The offline parity helper retains Manual’s removed zero fallback.** [autofit/parity.py:101](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/autofit/parity.py:101).

   With `E=[0,1,2,3,4,5]`, `I=[10,12,40,30,22,20]`, Manual without anchors, it returns six zeros; production now returns `[10,12,14,16,18,20]`. This reference no longer reproduces production.

Verification: **82 Python and 62 JavaScript tests passed** using read-only wrappers. Both round-8 fixes reproduced correctly. **128 loader round trips**, all four measurement summaries, the **3/62/56 census**, and **376 bit-identical Smart comparisons** passed. Lifecycle probes used extracted production functions; full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
