**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **No: the validator rejects some responses the server actually writes.**  
   Path: `individual_peaks[i].id`.

   Using the existing well-posed fixture, IDs `""`, `"é"`, `null`, `true`, and `false` each produced HTTP 200 from `/api/fit`, with `success: true` and completed scattered starts. Their unmodified responses then self-compared with HTTP 400.

   The ASCII/nonempty restriction and explicit boolean/null rejection are narrower than the producer’s accepted prefixes. This is an additional compatibility failure beyond the documented extreme-bound refusal. [fitting.py:243](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:243), [fitting.py:2773](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2773)

2. **Yes: malformed structures still reach comparison. Two further MINOR findings:**

   - **Link validation checks spelling without fully checking the target or numeric token.** Path: `individual_peaks[i].params[name].expr`. A Gaussian component `1` and GL component `2`, with component 2’s `gl_ratio` set to `vary=False, expr="p1_gl_ratio"`, pass validation although component 1 has no such parameter. Requests containing this response return 200 on side a, b, or both; self-comparison returns `same: true`. The validator searches component IDs without requiring the referenced parameter to exist. [fitting.py:264](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:264)

     Likewise, `p1_center + 1e+999` and `p1_center + 01` pass and self-compare `same`. Neither token is finite-float text as the producer writes it; the regex alone does not establish that property. [fitting.py:214](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:214), [fitting.py:1828](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1828)

   - **An empty component list is accepted.** Set `individual_peaks=[]` and `starts=null` on a real response. Validation returns `None`; a, b, and both return 200, with self-comparison `same: true`. The validation loops accept the empty list, whereas `run_fit` explicitly requires at least one component. [fitting.py:241](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:241), [fitting.py:2825](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2825)

   **I did not reproduce a new 500 with the current validator.**

3. **The round-9 finding is resolved.** Alternative parameter maps must now match their component’s exact parameter set, so the added `value`/`min`/`expr` names are refused before comparison. [fitting.py:289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:289)

   The comparator’s decision logic is unchanged: AST comparison against the former helper matched after accounting for documentation, renaming, and the assertion/return wrapper. Admitted real responses retain those comparison rules. However, finding 1 changes endpoint behavior for some real responses by refusing them before comparison. [app.py:1462](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1462), [app.py:1475](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1475)

4. **The tests establish their bounded regression claims, not the universal exact-structure claim.**  
   Validation completed with **173 passed, 1 skipped**, including the fuzz and current numerics-digest check. All **328 records** passed validation and self-compared `same`. Replacing the validator with the old form check failed all **72 hostile-case assertions**.

   The fuzz checks only whether status is 200 or 400. It has no independent assertion that a 200 input has valid structure, so its “200 means still a fit’s structure” claim is unsupported—and contradicted by finding 2. The real-fit matrix also uses fixed fixture IDs, missing finding 1. [tests/test_seal_1d_compare.py:275](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:275), [tests/test_seal_1d_compare.py:335](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:335)

Read-only execution used in-memory sessions and an enlarged regex cache for the chain tests. No files changed.

**VERDICT: NO-GO.**
