Reviewed `b804968..5aabcec`, focusing on the commit after `de35d7e`. **One MAJOR issue remains.**

1. **MAJOR — A project round trip loses the preserved historical area. No non-physical inputs required.**

   The [spectrum loader](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12441) retains historical areas in `fitResult._savedPeakAreas`, but the [project writer](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12179) omits that field. After reopening the project, `_ownFitArea()` falls back to the backend value or recomputation.

   Reproduced in memory with the page’s save/load functions, using committed `4-GTA UCl4-BN`, `B1s Scan_4`, and main’s spectrum-area calculation:

   - Historical spectrum area: **40119.7714413772**
   - Direct spectrum reload/save: **40119.7714413772** — fixed.
   - Spectrum → project save → project reload → spectrum save, without edits: **40119.771441377176** — rewritten.
   - The fit remains restored; labelled `displayArea` is **40127.762171894756**.

   Persist the historical area through project serialization. Extend the regression test to include this route. The numerical difference is tiny, but it violates the explicit requirement to preserve the saved value verbatim.

2. **MINOR — Implementation comments still present the superseded measurement artefact as real. No non-physical inputs required.**

   The [area-helper comments](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:9732) still say “Rectangular-rule” and cite the old `0.034 pp` / `17–19 %` findings without marking them superseded. The README and plan now explain these correctly.

Other review results:

- No remaining component rectangle integrator or additional grid/note defect found in the inspected paths and exercised tests. Results, sidebar, support patching, Quantify, CSV/XLSX and the graphite warning use the shared area path. Scattered-starts tables consume server areas; TSV, stack plots and publication figures do not independently report scalar component areas.
- Reproduced **530 component areas across 121 tabs** within floating-point rounding: median **0.006892%**, maximum **0.198027%**, maximum percentage change **0.008316645 pp**, zero outside-window components and no warning flips across 44 graphite models. Thus **≤0.0084 pp** is valid; **≤0.008 pp** is not. The README’s frame-artefact explanation is supported.
- The revised preservation test genuinely tests direct spectrum round-tripping. Export-prefix normalization proves compatibility with area semantics normalized, not literal historical numeric equality.
- No Q8 runtime implementation or unrelated production change found.

Validation: **98 focused JS tests passed**, plus eight lineshape-area tests with an in-memory temporary-directory initialization. Another **36 SciPy comparisons** matched exactly through 100,001 points; singleton and NaN checks passed. Browser tests were inspected, not executed. No files changed.

VERDICT: NO-GO
