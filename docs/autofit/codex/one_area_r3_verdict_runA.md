Reviewed `b804968..de35d7e`, focusing on the commit after `b0c4355`. **One MAJOR issue remains, plus one MINOR.**

1. **MAJOR — An unedited reload still rewrites its saved `area`. No non-physical inputs required.**

   The [save code](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12063) recomputes `area` from the reconstructed curve and `_modelBe`. The spectrum loader never retains the incoming `peakCurves[].area`, so adding `displayArea` does not preserve the historical value.

   Reproduced in memory using the actual `_loadSpectrumFile()`, restoration checker and `_doSaveSpectrum()`:

   - Ordinary ascending, 241-point legacy Gaussian: saved area **1064.4663789211602** becomes **1064.4670249740102**, with the component curve unchanged.
   - A larger example using non-monotonic sample order `[280,282,281]`, Gaussian centre 281, FWHM 1, amplitude 1,000: the previous save formula produces **656.25**; an unedited reload/save replaces it with **406.25** and adds `displayArea: 406.25`.

   The separate sealed `statistics.record` payload is forwarded unchanged. The violation is specifically the historical `peakCurves[].area`.

   The [new preservation test](/Users/skyefortier/xps-app/.claude/worktrees/one-area/tests/test_browser_one_area.py:121) does not prove its claim: it compares a reconstructed area against the absolute backend value within tolerance, without round-tripping an existing saved `peakCurves[].area`. Preserve that original field verbatim and test exact preservation; compute the labelled display value separately.

2. **MINOR — The plan still understates the measured bound. No non-physical inputs required.**

   [The plan](/Users/skyefortier/xps-app/.claude/worktrees/one-area/docs/superpowers/plans/2026-10-12-one-area-definition.md:26) still says “at most 0.008 pp.” The recorded maximum is **0.008316645126662081 pp**. Use “approximately 0.0083 pp” or a valid upper bound.

Other review results:

- No remaining component rectangle integrator found. Scalar readers use the shared area path; scattered-starts tables consume server areas. TSV, stack plots and publication figures do not independently report scalar component areas.
- The new signatures address successive stale edits and renamed outside-window notes. I found no additional grid-selection or note defect by inspection.
- **46 focused tests passed**, plus **eight lineshape-area tests** with an in-memory temporary-directory initialization required by the read-only environment. Another **42 arithmetic cases** matched SciPy exactly through 100,001 points; singleton and NaN behavior also checked out.
- Reconstruction reproduced all **530 component areas across 121 tabs** within floating-point rounding: median **0.006892%**, maximum **0.198027%**, zero outside-window components. Recorded warning comparisons show no flip. The README’s saved-frame artefact explanation is supported.
- The export-prefix override remains a valid **conditional compatibility test with area semantics normalized**, not proof of literal historical numeric equality.
- No Q8 refit implementation or unrelated runtime change found. Browser tests were inspected, not executed. No files changed.

**VERDICT: NO-GO**
