Reviewed `b804968..929212e`, focusing on round 5 after `5aabcec`. **No BLOCKER or MAJOR finding.**

**MINOR — Incorrect measurement command.** The usage text in [q5_areas_on_load.py](/Users/skyefortier/xps-app/.claude/worktrees/one-area/scripts/q5_areas_on_load.py:9) names nonexistent `scripts/outside_window_note_on_load.py`. It should name `scripts/q5_areas_on_load.py`. No non-physical inputs required.

Review results:

- **Round 4’s preservation defect is fixed.** Exercised the production project serializer, JSON round trip, restoration checker and area accessor with deliberately marked historical values. They survived exactly. JSON and ZIP saves share that serializer.
- No remaining component rectangle integrator, additional grid-selection defect, outside-window-note defect or historical-area rewrite found. Scattered-starts tables consume server fractions; TSV, stack plots and publication figures do not independently report scalar component areas.
- Independently reproduced **121 tabs, 530 components**, median change **0.006892%**, maximum **0.198027%**, maximum percentage change **0.008316645 pp**, and **zero noted components**, matching `on_load.json` within floating-point rounding. Thus **≤0.0084 pp** is correct; the prompt’s **≤0.008 pp** is not. The frame-artefact explanation is supported; the recorded 44 graphite comparisons show no warning flip.
- The export-prefix test validly checks compatibility **after normalizing area semantics**. It does not establish historical numerical equality, and its revised description acknowledges that.
- No Q8 runtime implementation or unrelated production change found.

Validation: **118 focused JavaScript tests and 49 lineshape tests passed**. Another **30 SciPy comparisons matched exactly**, through 100,001 points, including irregular and non-monotonic grids; singleton and NaN checks passed. Browser suites were inspected, not executed. No files changed.

VERDICT: GO
