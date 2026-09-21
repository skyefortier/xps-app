Reviewed fix `8d98752` against `main`. Actual HEAD, `8612eef`, only adds the review prompt. No files changed.

1. **MAJOR — The guard accepts bound-pinned Graphite when every component is near zero.** [templates/index.html:6830](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6830)

   Reproduced using extracted frontend model-building functions and the actual backend with `n_perturb: 3`:

   - CSV spectrum: 280–295 eV, 0.05 eV spacing, baseline 10 with a Gaussian bump of height 0.004 and FWHM 0.4 at 284.5.
   - Frontend detection accepts that bump. `uploadToBackend` rounds intensities to two decimals, so the backend receives **constant 10**. Linear background subtraction leaves **zero signal**.
   - `leastsq` reports success: Graphite amplitude **2.38e-12**, strongest amplitude **6.02e-12**, Graphite centre **284.22757**.
   - The new guard passes because `2.38e-12 > 6.02e-18`. The centre also passes validation, producing approximately **0.272 eV of global correction from numerical residue**.
   - `least_squares` also passes on this input, returning Graphite amplitude approximately `6.18e-5`.

   Thus `1e-6 × strongest` is useful for rejecting a negligible component beside substantial components, but cannot establish support when the entire fitted model vanishes. Add a zero-signal/all-components-negligible case and regression coverage.

2. **MINOR — Rollback leaves Custom reference controls hidden. Existing restore defect, reached by the new rejection.** [templates/index.html:6760](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6760)

   Start with Custom charge correction, then reject an Auto-Fit. The provisional `c1s` update hides `cc-target-field`; restoration reinstates `cc-method = custom` and its values but never restores field visibility. Reproduced with the extracted functions: the custom target remains `display: none`.

3. **MINOR — Rejection does not restore undo/redo history. Existing behavior.** [templates/index.html:6982](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6982)

   Undo an edit, then attempt an Auto-Fit that fails this guard. `pushUndo()` clears the redo stack and adds an undo entry; `_autoFitRestore` restores neither. The rejected operation therefore loses the previously available Redo.

The remaining requested checks:

- **Core rollback works:** verified restoration of peak values, `_backendParams`, `fitResult`, provenance, `nextId`, provisional `ccShift`, charge inputs, ROI/background endpoints, and manual anchors. The inactive-owner branch also restores those fields into the owning tab.
- **Placement is correct:** the guard precedes all final charge-input writes. The unchanged `<40%` amber warning remains on the success path.
- **Locked/linked amplitudes:** the generated Graphite has `fixAmplitude: false` and `linked: null`; existing user locks/links are replaced with the new model. They do not explain a false rejection here.
- **Threshold false rejection:** I found no demonstrated realistic, resolvable Graphite anchor incorrectly rejected in this bounded model. The reproduced false acceptance above is sufficient to invalidate the stated guarantee.
- **Rollback is the appropriate outcome:** Auto-Fit promises model plus charge correction. Retaining a fit in its provisional correction frame would require a separately designed partial-success outcome.
- **Other global centre paths:** no additional fitted-component-centre-to-charge-correction path found. The charge-reference checkbox only records a designation; batch propagation copies an existing shift.

All **9 new tests pass**. Additional checks used extracted JavaScript and the actual fitting backend; no browser run.

**VERDICT: NO-GO.**
