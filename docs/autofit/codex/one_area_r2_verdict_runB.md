Reviewed `b804968..b0c4355`, focusing on the fixes after `5319bf5`. **Two MAJOR issues remain.** Neither requires non-physical inputs.

1. **MAJOR — Displayed areas stop following edits while Results is already stale.**  
   The [refresh logic](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:8588) checks statistics state, unsupported IDs and outside-window IDs—not changes to areas or their grid.

   Executing the page’s extracted functions with a Gaussian at 280.5 eV, FWHM 1, over 280–290 eV:
   - Changing amplitude from 1,000 to 2,000 makes Results stale and displays **1,872.18**.
   - Changing it again to 3,000 leaves Results/Quantify at **1,872.18**, although the current calculation used by exports/save is **2,808.27**.
   - Narrowing the ROI while already stale likewise leaves the displayed number unchanged.

   Sidebar percentages also lack a refresh when the grid changes without a support-status change. Sharing `_areaGrid()` does not ensure that already-rendered readers agree. Refresh the numerical consumers when their model/grid changes, including successive stale edits.

2. **MAJOR — Restored spectrum saves still bypass the shared area grid.**  
   [Spectrum save](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12049) integrates unchanged restored fits on `own._modelBe`, while [_areaGrid()](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:9760) selects the live ROI for stale results.

   Reproduction using an ordinary Gaussian, centre 281 eV, FWHM 1, amplitude 1,000: fit over 280–281 eV, widen the ROI to 280–290, save the project and restore it. The actual restore checker accepts it; `_ownFit` is true:
   - Results/CSV area: **1,054.31571**
   - Spectrum-save area: **522.08220**

   This isolates the grid disagreement without legacy lineshape differences. Preserving historical curves is understandable, but that exception does not deliver the requested single area across readers. Historical and current-model areas need an explicit distinction or a consistent reporting rule.

3. **MINOR — “At most 0.008 pp” is not the measured bound.**  
   [The plan](/Users/skyefortier/xps-app/.claude/worktrees/one-area/docs/superpowers/plans/2026-10-12-one-area-definition.md:26) states that bound; the recorded maximum is **0.008316645 pp**. Use “approximately 0.008 pp” or report more digits. No non-physical inputs are involved.

The remaining checks support these conclusions:

- **Arithmetic:** SciPy parity passed, including ascending, descending, irregular and non-monotonic grids through 30,001 points, empty/single-point inputs and NaN propagation. I found no remaining component rectangle integrator.
- **Measurements:** Independent reconstruction reproduced the loaded component areas within floating-point rounding: **121 tabs, 530 components, median 0.006892%, maximum 0.198027%, 44 graphite models without a warning flip, zero noted components**. The README’s B–O frame-artifact explanation is supported. These are formula comparisons on the same selected grid; they do not establish agreement of every displayed/saved reader.
- **Note and state handling:** The new note refresh addresses the reported stale crossing case and supports no-fit results. Undo/history restoration explicitly rerenders. TSV, stack plots and publication figures do not independently report scalar component areas; scattered-starts areas originate on the server.
- **Tests:** The browser tests provide real but limited coverage. They omit restored-save disagreement and numerical agreement after successive stale edits. The export-prefix override remains valid as a **conditional compatibility test with area semantics normalized**, not literal historical numeric equality.
- **Scope:** No Q8 refit implementation or unrelated runtime change found.

Validation: **46 focused tests, eight new lineshape-area cases, and 37 additional arithmetic cases passed**. Browser tests were inspected, not run under this read-only environment. The generator completed with its write intercepted in memory. No files changed.

VERDICT: NO-GO
