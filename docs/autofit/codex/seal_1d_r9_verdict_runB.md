**One MINOR remains. No BLOCKER or MAJOR found.**

1. **Round-8 reproductions: fixed.** Duplicate IDs within alternatives are refused, and unsupported names in `individual_peaks[].params` are refused before comparison on either side. However, the parameter-name restriction remains incomplete. [app.py:1489](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1489), [app.py:1493](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1493)

2. **MINOR — alternative parameter maps can still cause HTTP 500.**  
   Path: `starts.alternatives[i].components[j].params`.

   These maps permit arbitrary numeric entries, and the new name check never visits them. [fitting.py:3332](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3332)

   **Reproduced:** starting with a response containing a valid alternative:

   ```python
   h = copy.deepcopy(response)
   h["starts"]["alternatives"][0]["components"][0]["params"].update(
       value=1.0, min=0.0, expr=1.0)
   client.post("/api/compare-fits", json={"a": h, "b": h})
   # HTTP 500
   ```

   Form validation passes. The comparator mistakes this map for parameter metadata, then passes numeric `expr` to `re.findall`, raising `TypeError`. [same_fit.py:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:247), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

   Placed only in **a** or **b**, this malformed map is compared with HTTP 200 and `starts.same: false`. Extend name validation to alternative parameter maps and add regression coverage.

3. **Real-fit compatibility: no additional refusal found.** All **328 stored records** self-compared `same`; the five real-fit offset tests passed. The allowed names match the producer, including its added `area`. The documented ±1e308 bound-span refusal remains. [tests:292](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:292), [fitting.py:3013](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3013), [plan:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:69)

4. **The new tests detect their named defects.** In-memory mutations removing either the name restriction or alternative-ID check failed its regression test. Replacing whole-text matching with prefix matching failed **seven grammar cases**. The alternative-map defect above is uncovered. [tests:300](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:300), [tests:311](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:311), [tests:281](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:281)

Validation: endpoint/comparator suite **92 passed, 1 skipped**; the skipped corpus check was separately verified against all 328 records. Browser tests were not rerun. No checkout files changed.

VERDICT: NO-GO
