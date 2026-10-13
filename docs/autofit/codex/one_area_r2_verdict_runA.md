Found **two MAJOR issues and one MINOR** in `b804968..b0c4355`. None requires non-physical inputs.

1. **MAJOR — Visible areas stop refreshing while Results is already stale.**  
   The [refresh logic](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:8587) updates Results when statistics state, support flags, or outside-window membership changes. Ordinary subsequent parameter edits can change none of these. Exports recompute areas; Results and Quantify retain earlier numbers. Sidebar percentages also lack a general refresh on parameter/ROI edits.

   Executing the page’s parameter-update, refresh and Results functions: Gaussian centred at 281 eV, FWHM 1, grid `[280,281,282]`; change amplitude from 1,000 → 2,000 → 3,000. The first edit displays **2,125**. After the second, Results/Quantify still hold **2,125**, while the current trapezoid—and export calculation—is **3,187.5**. Refresh numeric consumers when the model/grid changes, even when the note’s membership stays unchanged.

2. **MAJOR — Restored spectrum saves still bypass the shared grid.**  
   The [save’s `own` branch](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12049) integrates restored components on `_modelBe`; `_areaGrid()` chooses the live ROI for stale results. These can select different samples.

   Reproduced using the actual restoration and `_doSaveSpectrum()` functions on committed `4-GTA UCl4-BN.proj.zip`, `B1s Scan_4`, component B–N:

   - Results/shared-grid area: **40,127.762171894756**
   - Saved `peakCurves[].area`: **40,119.771441377176**

   `B1s Scan_1` also differs. These examples have **no legacy Voigt mismatch**. The save exception therefore still defeats the promised reader agreement.

3. **MINOR — Renaming a noted component leaves its old name in the note.**  
   The [note refresh comparison](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:8593) checks only IDs. With no fit, create an outside-window component named “Old name”, then rename it “New name”: Results continues saying **“Old name is centred outside…”**. Reproduced through the page’s update and rendering functions.

Other review results:

- **Arithmetic passed:** 46 focused tests, plus all eight lineshape-area cases using an in-memory temporary-directory initialization for this read-only environment. Additional SciPy comparisons passed through 30,001 points, including descending, irregular and non-monotonic grids. One-point and NaN behavior checked out.
- **Corrected measurements reproduce:** all **530 recorded areas across 121 tabs** matched exactly using the page’s restoration/integration functions; 81 fits retained, zero geometrically outside components. Median change **0.006892%**, maximum **0.198027%**. Maximum percentage change is **0.00831665 pp**—“0.008” is rounded, not a strict upper bound. Recorded warning comparisons show no flip.
- **The README’s B–O explanation is correct.** Reconstructed corrected windows contain the B–O centres; the earlier saved-frame measurement manufactured the outside-window finding.
- **Tests improved, but coverage remains incomplete.** The browser test checks agreement after fitting and one charge correction; subsequent edits check only note presence. It does not catch finding 1 or exercise restored spectrum saves. Browser tests were inspected, not executed here.
- **The export-prefix override remains valid conditionally:** it checks compatibility with area semantics normalized, not literal equality with historical numeric exports.
- No remaining component rectangle integrator found. Scattered-starts tables consume server areas; TSV, stack plots and publication figures do not independently report scalar component areas. No Q8 refit implementation or unrelated runtime change found.

No workspace files changed.

VERDICT: NO-GO
