Reviewed `b804968..de35d7e`, focusing on the changes after `b0c4355`. **Two MAJOR findings remain. Neither requires non-physical inputs.**

1. **MAJOR — An unedited spectrum save still rewrites its historical `area`.**  
   The [save calculation](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12063) recomputes `area`; the [spectrum loader](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12371) does not retain incoming `peakCurves[].area`.

   Executing main’s writer → HEAD’s loader → HEAD’s writer, without editing:
   - Committed `4-GTA UCl4-BN`, B1s Scan_4: **40119.7714413772 → 40119.771441377176**.
   - A derived case with finite, monotonic sampling variation below 0.00005 eV, accepted by restoration: **40120.21055371035 → 40119.771441377176**.

   `displayArea` is correctly added and labelled, and `_backendParams` remains intact. Nevertheless, the existing spectrum-area field changes, contrary to the owner’s preservation constraint. Retain the incoming historical area verbatim; compute the display value separately.

2. **MAJOR — The new preservation test does not test preservation of the saved area.**  
   The [test](/Users/skyefortier/xps-app/.claude/worktrees/one-area/tests/test_browser_one_area.py:121) loads a project, then compares the newly calculated spectrum area against `abs(_backendParams.area.value)` with a tolerance. It never loads a spectrum containing an existing `peakCurves[].area` and checks that the same value survives. It therefore permits finding 1 while claiming the historical area is unchanged. Add an actual save/load/save equality check, alongside the display-area assertion.

3. **MINOR — The strict measurement bound remains incorrect.**  
   The [plan](/Users/skyefortier/xps-app/.claude/worktrees/one-area/docs/superpowers/plans/2026-10-12-one-area-definition.md:26) still says “at most 0.008 pp”; the maximum is **0.008316645126662081 pp**. Likewise, `≤ 0.0083` in CLAUDE.md rounds downward. Use an approximate value or an upper bound. No non-physical inputs required.

Other review results:

- **Round 2’s refresh and rename failures are fixed in the exercised paths.** Executing the page’s refresh/render functions produced areas **1062.5 → 2125 → 3187.5** across successive stale edits, then **1593.75** after narrowing the ROI. Renaming updated the outside-window note.
- **Arithmetic passed:** SciPy parity, grid-direction and irregular/non-monotonic cases, single-point behavior, NaN propagation, and all eight lineshape-area cases. No remaining component rectangle integrator found.
- **Measurements reproduced within floating-point rounding:** **121 tabs, 530 components, 81 retained fits**, median **0.006892%**, maximum **0.198027%**, **44 graphite models with no warning flip**, and **zero outside-window components**. The README’s explanation of the earlier B–O frame artefact is supported.
- **Export-prefix normalization remains a valid conditional compatibility test.** It checks unchanged surrounding export content with area semantics normalized; it does not prove literal historical numeric equality.
- TSV, stack plots and publication figures do not independently report scalar component areas; scattered-starts fractions originate on the server. No Q8 runtime implementation or unrelated production change found.

Validation: **46 focused tests passed normally; eight lineshape-area tests passed with in-memory temporary-directory initialization.** Browser suites were inspected, not executed in this read-only environment. No files changed.

VERDICT: NO-GO
