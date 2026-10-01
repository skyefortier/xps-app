# Background math implementation round 2 — run B (commit cf64e80; codex exec, reasoning high)

1. **BLOCKER — Restored fits still use uncertified stored curves.** [templates/index.html:9558](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9558), [templates/index.html:9583](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9583).  
   With `E=0..11`, `I=[10,15,10,20,50,80,60,40,30,25,20,20]`, Shirley averaging 3, main’s stored background fails today’s certificate by **0.258% of the intensity span**. Nevertheless, `_restoredFitBgFailure` returns `null` because a *new* background converges; stack Path A/A2 then draws the old curve unchanged. I reproduced both results. The KEEP policy is stated honestly in §1, but certifying a different curve does not satisfy “nothing downstream treats it as valid.” The browser test exercises rejection only; it misses this retained-fit case.

2. **MAJOR — Reloading can discard valid manual-background fits.** [templates/index.html:9547](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9547), [templates/index.html:9486](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9486).  
   The new restoration gate reuses a stack helper that silently substitutes **Shirley for manual** and ignores saved anchors. For `E=[4,3,2,1,0]`, `I=[20,5,1,5,10]`, a saved manual background with anchors `(0,0),(4,0)` is well-defined. Restoration instead returns “Shirley background not converged … no net signal,” causing the fit and support verdicts to be dropped. This affects both project and spectrum-file loading.

3. **MINOR — The strengthened class guard still permits consumption without refusal.** [tests/js/background_not_converged.test.js:70](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/js/background_not_converged.test.js:70).  
   Both in-memory mutations passed the actual guard:
   - Assign the background, put its first `_bgFailure(bg)` reference inside `if (false)`, then consume it.
   - Consume through `const bg = computeBackground(...).map(...)`, then check `bg`.

   The guard neither establishes control flow nor inspects consumption on the assignment line. Round-1 finding 7 remains incomplete.

4. **MINOR — “Bit-identical … every method” overclaims manual parity.** [plan:78](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:78), [templates/index.html:14883](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:14883).  
   For manual anchors `(0,0.1),(3,3.2)` at energy `1`, the page returns `1.1333333333333337`; the server’s interpolation returns `1.1333333333333335`. This pre-existing, negligible rounding difference contradicts the newly broadened claim; qualify it or cover manual explicitly.

Validation: **64 Python and 45 JS checks passed**. All four analysis summaries reproduced exactly, including the seeded maxima and **two better / four worse / two level** classification. Serialization matched the page on all 202 targets; all **376 Smart/Smart-experimental pairs were bit-identical**. HTTP/browser suites were not rerun under the read-only constraints. No files changed.

**VERDICT: NO-GO.**
