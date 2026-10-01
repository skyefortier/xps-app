# Background math implementation round 1 — run A (commit 0571228; codex exec, reasoning high)

1. **BLOCKER — Restored fit backgrounds bypass certification.** [templates/index.html:10025](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10025), [templates/index.html:9520](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9520).  
   Load a project containing the old Shirley fit for `E=[0,1,2,3]`, `I=[2,3,10,13]`. Its background misses the relation by **14.3% of the span**, but `haveFit` selects the stored arrays despite the live failure. Stack Path A/A2 likewise draws them without checking. Project loading restores `fitResult` verbatim; Quantify and project saving continue consuming it. I reproduced the stack rendering the failed curve after JSON serialization. Array certificate properties disappear during serialization, and `_bgFailure` treats an absent certificate as success. This violates “nothing downstream treats it as valid.”

2. **MAJOR — Tougaard certifies a non-solution, and page/server verdicts disagree.** [fitting.py:889](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:889), [templates/index.html:4600](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4600).  
   The certificate checks determinacy using the server’s approximate loss sum; it never checks the supplied curve against the defining sum. With averaging 1:
   - `E=[0,1,2.0000005,3.0000005]`, `I=[2,3,0.008279338821039262,3]`: both certify, but server/page interior backgrounds are **1002.0000000000546 / 1001.5074012756077**, differing by **16.47% of the intensity span**.
   - Change the third intensity to `0.007279338821039261`: the server refuses as unsolvable; the page certifies `[2,2,2027000.4816686625,3]`.
   
   These reproduce the accepted findings’ near-cancellation cases. The plan’s exemption for the approximation does not satisfy the owner’s every-background requirement.

3. **MAJOR — Linear’s known non-solution is newly marked certified.** [templates/index.html:4597](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4597).  
   `computeBackgroundCore([0,1,3],[10,20,40], linearSettings)` returns `[10,25,40]` with `converged:true`. Its stated affine-in-energy background—and the server’s answer—is `[10,20,40]`. The unconditional success for explicit methods permits the page to subtract, fit locally and export this incorrect curve. The arithmetic discrepancy predates this unit; certifying it under item 2 is the acceptance failure.

4. **MAJOR — The measurements do not isolate item 1 from item 3.** [scripts/bg_math_impl_measure.py:32](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/scripts/bg_math_impl_measure.py:32).  
   `levels_abs` restores the tolerance magnitude but retains the new **return-before-update** behavior; main returned the updated iterate. At averaging 1, `E=0..5`, `I=[10,12,40,30,22,20]`, this supposedly averaging-only variant changes the background by `3.815904605630749e-7`. That can redraw the request seed. Indeed, §4 attributes its **28.44 pp** maximum to item 1 on a target saved at averaging **1**, where averaging changes nothing. Re-run the isolated comparison with main’s stopping/return semantics preserved.

5. **MINOR — Stop and certificate disagree at the tolerance boundary.** [fitting.py:919](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:919).  
   For `E=[0,1,2,3]`, `I=[0,0,7.326101243535137,2.1978303730605416e-11]`, Shirley stops immediately because `diff <= tolerance*span`. The certificate divides first, obtains `1.0000000000000002e-12`, and rejects it. Its message incorrectly says the iteration alternated or exhausted its steps. Use the identical comparison predicate for stopping and certification, including the page twin.

6. **MINOR — The claimed class guard is unsound.** [tests/js/background_not_converged.test.js:33](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/js/background_not_converged.test.js:33).  
   `return computeBackgroundCore(...).map(...)`, `(computeBackgroundCore)(...)`, aliases and helper-returned backgrounds evade detection. For matched assignments, merely mentioning `_bgFailure(variable)` anywhere in the function passes—even in an unreachable branch or after consumption. The existing stack function demonstrates the control-flow hole: its check covers Path B while Path A/A2 remains unchecked.

Focused verification: **61 Python and 31 JS tests passed**; API/browser tests were not rerun. All four analysis summaries reproduced exactly, and all **376 committed Smart/Smart-experimental pairs were bit-identical**. The reported 40,000-case random experiment was not independently reproduced. No files changed.

**VERDICT: NO-GO.**
