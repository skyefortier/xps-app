Both round-1 **MAJOR** findings are fixed. Two **MINOR runtime defects** remain: malformed inputs can still produce HTTP 500. No BLOCKER or remaining MAJOR found.

1. **Round-1 findings**

   | Finding | Status |
   |---|---|
   | Re-run changes the page’s numerics and invalidates verification | **Resolved.** The caller passes `noteSoftware: false`, and `_serverFitJob` honors it. [index.html:9718](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9718), [index.html:8658](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:8658). |
   | Numerics compared against the comparison worker | **Resolved.** Comparison uses `a.software` versus `b.software`, iterating every `NUMERICS_IDENTITY_KEYS` field. [app.py:1493](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1493). |
   | `10**400` reaches comparison and returns 500 | **Specific defect resolved**, including either side and both tested locations. Broader input refusal remains incomplete; see answer 4. [app.py:1474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1474). |
   | Comparison reply retained after replacement | **Resolved.** Ownership is checked after the final await/error handling, immediately before storage. [index.html:9740](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9740). |
   | Edits/tab switches do not discard despite the plan | **Explicit scope amendment, implemented.** The outcome belongs to the record and is hidden while edited. [plan:41](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:41). **MINOR documentation inconsistency:** the Tests paragraph still describes edit/tab-switch discard. [plan:64](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:64). |
   | Missing regression coverage | **Resolved for the named defects**, with limits described in answer 5. |

2. **Can a re-run change the listed state outside its outcome?**

   **No remaining path found.** Software tracking is suppressed; the result goes into `_rerunOutcomes`, without installation or model mutation. Saves serialize the seal, and export wording reads the existing seal state—not the re-run outcome. Transient job bookkeeping and repainting still occur. [index.html:9741](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9741), [index.html:13728](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:13728), [index.html:9787](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9787).

3. **Can an outcome be kept or shown for another fit?**

   **No path found.** Storage checks the original live owner and exact seal identity. Rendering retrieves the outcome by that seal and requires the fit to be displayed as recorded. Edits hide it; switching tabs preserves ownership; replacement or closure before completion discards it. [index.html:9740](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9740), [index.html:9752](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9752), [index.html:9621](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9621).

4. **Is every malformed/hostile input refused with 4xx?**

   **No. Two reproduced MINOR defects remain.**

   **MINOR — bound-span overflow.** Starting with a real response, set a floating-valued `fwhm` parameter’s integer bounds to `min = -10**308`, `max = 10**308`, then compare identical copies. Both bounds pass `_floats_only`, but their integer difference overflows when multiplied by the floating tolerance. The endpoint returns **500**, even for identical sides. [app.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1454), [same_fit.py:199](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:199).

   **MINOR — link-chain recursion.** Add 1,100 otherwise correctly shaped parameter entries whose expressions form a chain of links, with null bounds. The shallow JSON passes validation, but `linked_bounds` recursively follows the chain and raises `RecursionError`. This also returns **500**. The request was approximately 269 KB, well below the body cap. [same_fit.py:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:141), [app.py:1488](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1488).

   The new recursion handling covers JSON parsing and `_floats_only`; it does not cover input-driven recursion inside comparison.

5. **Do the new tests fail on their named defects?**

   **Yes for the targeted regressions, with a browser-execution limitation.** All **13 server cases passed** using in-memory upload/session storage. Removing numeric validation made both new numeric cases fail; restoring comparison-worker identity made the new numerics test fail. [test_seal_1d_compare.py:113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:113).

   The browser tests now target the actual changed-software polling reply and replacement during comparison. Their assertions catch the named defects. An extracted-page JavaScript harness passed normal, replacement, closure, edit and tab-switch scenarios, and rejected mutations restoring software tracking or late-outcome retention. **The full browser suite was not run** under the read-only constraints. [test_browser_seal_1d.py:146](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_browser_seal_1d.py:146), [test_browser_seal_1d.py:172](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_browser_seal_1d.py:172).

   All **37 unchanged comparator tests passed**. Neither new input-driven 500 is covered.

No files changed.

VERDICT: NO-GO.
