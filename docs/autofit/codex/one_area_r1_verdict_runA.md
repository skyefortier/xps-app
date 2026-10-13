**The formula switch is correct, but the unit does not deliver the server’s area everywhere.** I found these issues in `b804968..5319bf5`. All reproductions below use ordinary finite inputs; none requires non-physical inputs.

1. **MAJOR — Readers still integrate in different energy frames.**  
   [Results](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:9830) uses the frozen `fitResult.be`; the sidebar, support patching and ordinary spectrum save use the live ROI. Charge correction shifts peak centres without shifting `fitResult.be`.  
   Reproduction: Gaussian, centre 280.5, FWHM 1, amplitude 1000, grid 280–290 at 0.1 eV; apply a +1 eV correction. Results/table export calculate **128.38**, while sidebar/spectrum save calculate **936.09**. Results also falsely labels the component outside the window. This is a manual charge-correction case, independent of Q8.

2. **MAJOR — Restored legacy fits still use the wrong integration grid.**  
   The restore distinguishes the server’s rounded `_modelBe` from reconstructed `be`, but [spectrum save](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:12023) evaluates on `_modelBe` and integrates against `be`. Results evaluates and integrates on `be`.  
   I constructed a keyed legacy Gaussian fit that the actual restore accepts as **current**: raw energies `280.00004 + i × 0.010001`, 101 points; centre 280.00002, FWHM 0.3, amplitude 1,000,000. The server-grid area is **159690.01**, Results gives **159650.06**, and spectrum save gives **159630.28**. The note also incorrectly marks the centre outside: it is inside the server’s rounded window.

3. **MAJOR — The new note stops updating once Results is already stale.**  
   [The note](/Users/skyefortier/xps-app/.claude/worktrees/one-area/templates/index.html:9867) only updates during `renderResults()`. Parameter edits repaint the chart, but `_refreshStatsState()` rerenders Results only when its statistics-state label changes.  
   Reproduction: make the result stale while a component remains inside, then move it outside. The note remains absent. Moving an already-noted component back inside similarly leaves the warning displayed. A forced Results render corrects it.

4. **MAJOR — “8 saved components get the note” does not measure the loading behavior.**  
   [The census](/Users/skyefortier/xps-app/.claude/worktrees/one-area/scripts/outside_window_census.js:30) bypasses restore validation and Results’ no-fit early return. All eight identified B–O tabs lack fitted envelopes, so the loader drops their fit results and Results never reaches the note.  
   Applying the actual restore checker across the measured corpus gave **121 tabs, 40 dropped fits, 81 retained fits, zero components eligible for the displayed note**. Eight is the geometric count before restoration, not the number receiving the note after loading.

5. **MAJOR — The “every reader” test does not establish its advertised guarantee.**  
   [The test](/Users/skyefortier/xps-app/.claude/worktrees/one-area/tests/js/one_area.test.js:45) checks source patterns, not reader outputs or grid selection. It even omits support patching from its enumerated functions. It passes with the contradictory numbers above. Add behavioral assertions covering reader agreement, charge correction, restored `_modelBe`, and note refresh.

6. **MINOR — The measurement generator is broken at HEAD.**  
   [Its extraction list](/Users/skyefortier/xps-app/.claude/worktrees/one-area/scripts/q5_area_definitions.js:30) omits `_trapezoidArea` and `_npPairwiseSum`, causing `ReferenceError`. Simply adding those dependencies would also make its supposed rectangle baseline call today’s trapezoid. Preserve an explicit historical rectangle calculation.

Other review results:

- `_trapezoidArea` matched SciPy on the tested ascending, descending, irregular and non-monotonic grids, including additional grids through 30,001 points. One-point and NaN behavior checked out.
- The archived numerical measurements reproduce exactly against the baseline page: **530 components; median 0.0073888%; maximum 0.0335387 pp**. Their interpretation as universal reader behavior is too broad.
- I found no remaining component rectangle integrator. Quantify inherits Results’ areas; scattered-starts tables consume server areas. TSV, stack plots and publication figures do not report integrated component-area numbers.
- The modified export-prefix test remains a reasonable **conditional layout/content regression test after normalizing area semantics**. It no longer proves literal historical export equality. I reviewed it but did not execute the browser test.
- **45 focused tests passed**, plus all **8 new lineshape-area tests** using an in-memory temporary-directory workaround for the read-only environment.
- No unrelated runtime change or Q8 refit implementation was introduced. No workspace files were changed.

**VERDICT: NO-GO.**
