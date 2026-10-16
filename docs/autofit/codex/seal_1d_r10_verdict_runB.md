**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **No: the validator rejects some successful server responses.**  
   **MINOR — component-ID compatibility.** I reproduced `POST /api/fit → 200, success: true` with IDs `""`, `"é"`, `true`, `false`, and `null`. Comparing each returned response with itself gives 400. The producer builds an lmfit prefix from the ID, while the validator imposes a narrower ASCII/nonempty/nonboolean domain. This contradicts acceptance of every response the server writes. [fitting.py:2773](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2773), [fitting.py:243](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:243)

2. **Yes: malformed structures still reach comparison on either side.**

   **MINOR — link validation does not establish a producer-valid link.** The check matches against component IDs without checking that the target component actually owns the named parameter. A GL component’s `gl_ratio` can reference `p2_gl_ratio` while component 2 is Gaussian and has no such parameter. The producer also prohibits links across different lineshapes. [fitting.py:264](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:264), [fitting.py:1735](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1735)

   Additionally, `individual_peaks[i].params.center.expr` accepts `p1_center + 1e+9999` and `p1_center + 00.5` with `vary: false`. Neither numeric spelling comes from the producer’s float formatting; the regex neither checks finiteness nor canonical spelling. [fitting.py:214](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:214), [fitting.py:1828](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1828)

   **MINOR — representability only checks overflow.** Setting `counts[0] = 9007199254740993` passes, although converting it to float changes its value. `_representable` discards the conversion result without checking equality. [fitting.py:224](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:224)

   I reproduced **200 on side a, side b, and both** for these malformed inputs; comparing each with itself returns **`same: true`**. I did **not** reproduce a new 500.

3. **The round-9 finding is resolved.**  
   Alternative parameter maps must now contain exactly their component’s parameters. Using original record 92, adding `value`/`min`/`expr` produces 400 on a, b, and both. [fitting.py:284](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:284)

   AST comparison confirmed that the comparator retains the former helper’s logic, apart from returning the problem list and adding the assertion wrapper. For admitted real responses, its decisions are unchanged. Endpoint eligibility **has** changed: the real responses in finding 1 are now refused. [same_fit.py:121](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:121), [same_fit.py:291](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:291)

4. **The tests support the measured claims, not universal structural correctness.**  
   Read-only execution using in-memory sessions: **173 passed, 1 skipped**, including the 3,000-mutation fuzz, all 328 supplied records, comparator tests, and numerics-digest checks. Replacing the validator with the old form check also failed all 72 hostile-case tests.

   However, the fuzz accepts either 200 or 400 without independently establishing which response is correct. It therefore cannot detect malformed inputs incorrectly compared with 200. [tests/test_seal_1d_compare.py:334](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:334)

   The lineshape matrix uses one method, background, and ratio; the corpus contains only `least_squares` responses and no non-null `required` results. These are useful compatibility samples, not coverage of every requested variant. [tests/test_seal_1d_compare.py:274](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:274)

No checkout files changed.

**VERDICT: NO-GO.**
