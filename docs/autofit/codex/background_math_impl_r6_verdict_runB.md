# Background math implementation round 6 — run B (commit 65da2c7; codex exec, reasoning high)

Reviewed `65da2c7`, read-only.

1. **MAJOR — Unsorted grids certify a Tougaard curve that violates its statement.** [templates/index.html:4598](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4598), [fitting.py:757](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:757).  
   For `E=[3,1,2,0]`, `I=[20,12,40,10]`, averaging 1, both sides certify `[20,18.827309233811235,10,10]`. At energy 1, the stated lower-energy loss sum must give background **10**: the only lower-energy sample has zero net intensity. Instead, the implementation includes the energy-2 sample because it follows energy 1 in the array. I reproduced successful server fitting, spectrum restoration, and stack rendering against this invalid curve. Preserving file order needs a monotonicity check before integral-background certification.

2. **MAJOR — Stack background subtraction uses the wrong samples on unsorted records.** [templates/index.html:9594](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9594), [templates/index.html:9850](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9850).  
   Load `E=[10,6,8,5,4,3,2,1,0]`, `I=10E`, linear background, ROI maximum 4. The valid restored ROI background is `[40,30,20,10,0]`. `_alignRawToFitBe` stops searching prematurely and supplies `[60,80,50,40,30]` as its raw intensities. Consequently, the stack’s background-subtracted trace is **`[20,50,30,30,30]` instead of five zeros**. Reproduced through the restoration and stack-render-data functions.

3. **MAJOR — Missing manual anchors silently select zero on the server.** [fitting.py:2047](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2047), [fitting.py:2066](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2066).  
   With `E=[0,1,2,3,4,5]`, `I=[10,12,40,30,22,20]`, a manual fit with omitted/null `manual_bg` returns **`success:true` against six zeros**. Passing `manual_bg=[]` instead uses `[10,12,14,16,18,20]`, matching the page’s documented fewer-than-two-anchor fallback. The API passes an omitted field through as `None`; `compute_background_only(method="manual")` also returns zero. These paths neither implement that fallback nor report failure.

4. **MAJOR — Overflowing certificate arithmetic accepts a non-solution.** [fitting.py:958](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:958), [templates/index.html:4657](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4657).  
   For `E=[0,1,2,3,4]`, `I=[1e308,-1e308,1e308,-1e308,1e308]`, Shirley + linear, averaging 1, both producers accept the constant background `1e308`. With equal edge levels, its defining statement gives `min(L,I)=I`, so that curve plainly fails. Both `span` and `diff` overflow; **`Infinity <= Infinity` certifies it**, despite a NaN residual. The returned values are finite, so round 5’s final finiteness check cannot catch this.

5. **MINOR — Anchor validation remains incomplete.** [templates/index.html:4858](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4858), [fitting.py:599](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:599).  
   A lone anchor containing NaN, Infinity, null, or a boolean bypasses validation and silently takes the linear fallback on both sides. Separately, `manual_bg=[null,[5,0]]` raises Python `TypeError` at `len(p)` instead of the promised `BackgroundNotConverged`; the page returns the intended plain refusal. These do not establish another invalid curve being consumed, but contradict the advertised validation behavior.

6. **MINOR — Manual-fallback overflow messages still differ.** [templates/index.html:4839](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4839), [fitting.py:2054](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2054).  
   Manual with no anchors, `E=[0,1e-309]`, `I=[0,1]`: the page says **“Manual background not converged…”**; the server’s linear fallback says **“Linear background not converged…”**. Both correctly refuse.

Verification: **68 Python and 72 JS checks passed**, including numerical and certificate parity. All four measurement summaries and the **3 restored / 62 different / 56 missing** census reproduced exactly. Another **242 committed-spectrum/averaging Smart comparisons** matched bit-for-bit and in verdict. Lifecycle probes used extracted production functions in memory; HTTP/browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
