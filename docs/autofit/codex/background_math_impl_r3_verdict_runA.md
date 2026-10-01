# Background math implementation round 3 — run A (commit 056a3ce; codex exec, reasoning high)

1. **BLOCKER — Changing the saved method bypasses certification of a stale fit.** [templates/index.html:9568](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9568).  
   The exemption reads the **current UI method**, not the method that produced the frozen fit. On `E=[5,4,3,2,1,0]`, `I=[20,22,30,40,12,10]`, the old five-step, save-rounded Shirley curve fails certification with residual **2.436e-6 of the span**. Change the method to `none` before saving that old fit: restoration accepts it, and stack Path A/A2 draws the rejected Shirley curve unchanged. `manual` also bypasses the check.

2. **MAJOR — Current spectrum-file fits lose their saved background during loading.** [templates/index.html:11212](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11212).  
   `_loadSpectrumFile` never transfers `data.roiBE` and `data.background` into `fr.be` and `fr.bgIntensity`. The new gate therefore drops valid `.spec.json` fits, claiming their background was not saved. I reproduced this for **Shirley, Smart, Smart experimental, Shirley + linear, Tougaard and linear**. Manual fits survive the exemption, but stacks then reconstruct Shirley: saved zero anchors `(0,0),(5,0)` produced a stack background spanning **10–20**, instead of zero.

3. **MAJOR — Restoration selects different ROI points than fitting does.** [templates/index.html:9537](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9537).  
   With descending `E=[5,4,3,2,1,0]`, set ROI minimum `2` and leave maximum blank. `getROIData` fits `[5,4,3,2]`; `_recordBackground` selects all six points because it requires both bounds to be finite. A current linear fit consequently fails reload. Ascending project data with an interior ROI also selects the wrong points because this helper assumes descending order. Both project formats share this gate.

4. **MAJOR — A nonnumeric stored sample makes the equality check fail open.** [templates/index.html:9579](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9579).  
   For the six-point spectrum above, a project background `[500,500,"bad",500,500,500]` passes restoration. The string makes `worst` become `NaN`, so `worst > 0` is false—even after large mismatches. The certified curve replaces the bogus background while the old `fittedY`, statistics and support records survive. I reproduced acceptance with unchanged `fittedY=[500,…]` and `chiReduced=0.01`.

5. **MINOR — The tightened class guard still accepts consumption without refusal.** [tests/js/background_not_converged.test.js:89](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/js/background_not_converged.test.js:89).  
   These mutations pass the actual guard: assign `const failure = _bgFailure(bg)` and ignore it; put `if (_bgFailure(bg)) return` inside a multiline `if (false) { … }`; or discard an inline `_bgFailure(computeBackground(...))` before computing and consuming another background. Recognizing the statement’s prefix does not establish refusal.

6. **MINOR — “No older saved fit is restored” is plainly presented but false.** [plan:103](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:103).  
   Using the actual pre-unit page code, `E=[5,4,3,2,1,0]`, `I=[100020,100022,100030,100040,100012,100010]`, five Shirley iterations save as `[100020,100020,100018,100014,100010,100010]`. This matches today’s six-significant-figure rounding and **is restored**. Manual and none also have explicit exemptions. The 0/65 observation cannot establish the universal consequence offered for the owner’s decision.

Verification: **73 Python and 44 JS checks passed**, including background/certificate parity and manual parity. All four measurement summaries reproduced exactly; all **376 Smart/Smart-experimental pairs were bit-identical**. Lifecycle reproductions used extracted page functions in memory; HTTP/browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
