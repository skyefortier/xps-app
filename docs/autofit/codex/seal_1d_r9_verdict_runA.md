**One MINOR remains. No BLOCKER or MAJOR found.**

1. **Both specific round-8 findings are resolved.** Duplicate IDs within each scattered-start alternative are refused on either side. Unsupported names in `individual_peaks[*].params` are also refused before comparison. [app.py:1489](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1489), [app.py:1493](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1493)

2. **MINOR — the parameter-map confusion remains in scattered-start alternatives, causing HTTP 500.**  
   Path: `starts.alternatives[i].components[j].params`.

   Alternative parameter maps accept arbitrary names with numeric values; the new name check covers only `individual_peaks`. [fitting.py:3332](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3332), [app.py:1493](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1493)

   Reproduced using stored record 92, whose unmodified self-comparison returns both verdicts `same`:

   ```python
   h = copy.deepcopy(O)
   h["starts"]["alternatives"][0]["components"][0]["params"].update(
       value=1.0, min=0.0, expr=1.0
   )
   # POST /api/compare-fits {"a": h, "b": h} → 500
   ```

   Form validation returns `None`. The comparator mistakes this map for parameter metadata and passes numeric `expr` to `re.findall`, raising `TypeError`. The failed curve reconstruction does not prevent this subsequent traversal. [same_fit.py:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:247), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

   Extend name validation to alternative parameter maps, or restrict metadata interpretation to actual parameter records, and add this regression. I reproduced no additional scale or link-graph bypass.

3. **Real-fit compatibility:** the documented refusal for extreme arithmetic, including ±1e308 bounds, remains. No additional refusal found: all **328 stored records** and all **five real-fit offset cases** passed. [plan:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:69), [tests:192](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:192), [tests:210](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:210)

4. **The new tests detect their named defects.** In-memory mutations confirmed that removing either new check fails its corresponding regression; replacing `fullmatch` with `match` fails seven grammar cases. The alternative-parameter 500 above is uncovered. [tests:281](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:281), [tests:300](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:300), [tests:311](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:311)

Validation: **93 endpoint/comparator tests passed**, using in-memory sessions. Browser tests were not rerun. No checkout files changed.

VERDICT: NO-GO
