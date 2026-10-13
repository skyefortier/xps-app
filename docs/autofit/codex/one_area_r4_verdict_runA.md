Reviewed `b804968..5aabcec`, focusing on round 4 after `de35d7e`. **One MAJOR issue remains.**

1. **MAJOR — A project save loses the historical area retained by this fix. No non-physical inputs required.**

   The [spectrum loader](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12441) retains `peakCurves[].area` in `_savedPeakAreas`, but the [project serializer](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12179) omits it. After project reload, `_ownFitArea` falls back to another value.

   Reproduced in memory using the production spectrum loader, save functions and restoration checker, with committed `4-GTA UCl4-BN`, **B1s Scan_4**:

   - Unedited spectrum reload/save preserves **40119.7714413772**.
   - Save that tab as a project, reload, then save its spectrum: **40119.771441377176**.
   - Both restoration checks succeed; `displayArea` is separately **40127.762171894756**.

   The difference is tiny, but the owner explicitly requires exact preservation. Persist the original areas through project JSON/ZIP saves and add this intermediate-project round-trip regression. The new direct spectrum round-trip test genuinely tests its claim; it misses this path.

2. **MINOR — A source comment still presents the superseded measurement artefact as real. No non-physical inputs required.**

   [The area-function comment](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:9746) still cites `0.034 pp` and “17–19% for a component centred outside the window.” Update it to the corrected measurement and frame explanation.

Other review results:

- No remaining component rectangle integrator found. No additional grid-selection or outside-window-note defect found. Scattered-starts fractions originate on the server; TSV, stack plots and publication figures do not independently report scalar component areas.
- Reproduced **530 component areas across 121 tabs** within floating-point rounding: median **0.006892%**, maximum **0.198027%**, maximum fraction change **0.008316645… pp**, and **zero noted components**. The recorded 44 graphite comparisons show no warning flip. The README’s frame-artefact explanation is supported.
- Export-prefix normalization validly checks compatibility with area semantics normalized; it does not prove historical numerical equality.
- No Q8 runtime implementation or unrelated production change found.

Validation: **98 focused JavaScript tests and 49 lineshape tests passed**, plus **33 additional exact SciPy comparisons** through 100,001 points and NaN/singleton checks. Lineshape tests required in-memory temporary-directory initialization for this read-only environment. Browser suites were inspected, not executed. No files changed.

**VERDICT: NO-GO**
