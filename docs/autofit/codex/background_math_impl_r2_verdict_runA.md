# Background math implementation round 2 — run A (commit cf64e80; codex exec, reasoning high)

1. **BLOCKER — Restored curves still bypass certification.** [templates/index.html:9558](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9558).  
   `_restoredFitBgFailure` certifies a newly computed background, then retains the old curve. For `E=[5,4,3,2,1,0]`, `I=[20,22,30,40,12,10]`, the old page’s five-step, save-rounded Shirley background fails the current certificate with residual **2.436e-6 of the span**. Nevertheless, restoration returns no failure and stack Path A/A2 draws that rejected curve. The policy is honestly documented, but it does not satisfy “check each result” or “nothing downstream treats it as valid.” The browser test covers rejection when recomputation fails, not this surviving bypass.

2. **MAJOR — Restoration discards valid manual-background fits.** [templates/index.html:9486](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9486), called by the new restoration check.  
   `_computeBackgroundForSource` substitutes Shirley for manual backgrounds and ignores saved anchors. With `E=[4,3,2,1,0]`, `I=[20,17,5,5,10]`, and manual anchors `(0,0)` and `(4,0)`, the page certifies the valid zero background. Restoration instead reports **“Shirley background not converged”** and drops the fit and support verdicts. This affects both project and spectrum-file loading.

3. **MINOR — The class guard still accepts unreachable checks.** [tests/js/background_not_converged.test.js:69](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/js/background_not_converged.test.js:69).  
   An in-memory mutation containing the following consumer passes the actual guard:
   ```js
   const bg = computeBackground(be, inten);
   if (false) _bgFailure(bg);
   return bg.map(v => v + 1);
   ```
   The first textual reference does not establish a refusal before consumption. The round-1 control-flow finding remains unresolved.

4. **MINOR — “Every method” bit-identity remains overclaimed.** [plan:78](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:78), [templates/index.html:14884](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:14884).  
   For manual anchors `(0,0)`, `(3,1)` evaluated at `E=[0,1,3]`, the page returns interior value **0.33333333333333337**; the server’s `np.interp` returns **0.3333333333333333**. This is negligible numerically, but disproves the unconditional claim.

Verification: **64 Python and 23 JS tests passed**. An additional **2,160 comparisons** across the five integral methods and linear had identical arrays and certificate verdicts. All four measurement summaries reproduced exactly; serialization matched the page for all 202 committed targets. HTTP/browser suites were not rerun under the read-only restrictions. No files changed.

**VERDICT: NO-GO.**
