Reviewed code commit `8d98752` against `main`. Actual HEAD, `8612eef`, only adds the review prompt. No files changed.

- **MAJOR — Relative threshold accepts an entirely collapsed model.** [templates/index.html:6830](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6830). When Graphite has the largest amplitude, *any positive value* passes—even numerical residue near zero.

  Reproduced using the shipped backend, Auto-Fit’s five-component model and bounds, default `least_squares`, and `n_perturb: 3`. Synthetic scan: 278–296 eV at 0.05 eV spacing; background 1000 counts plus a 30-count Gaussian bump at 284.5 eV, FWHM 0.3 eV; manual background set to 1020 counts. This represents a weak scan with an overestimated background. The positive bump passes initial peak detection.

  Backend returned `success: true`, amplitudes `[3.25e-8, 2.59e-10, 1e-10, 1e-10, 1e-10]`, and Graphite centre `284.200000028`. **The guard accepts this and permits an approximately 0.3 eV global correction from an effectively absent component.** The support scale needs an independent data reference or equivalent protection against all components collapsing.

- **MINOR — Rollback leaves Custom reference controls hidden.** [templates/index.html:6760](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6760). Start with Custom charge correction, then run an Auto-Fit that rejects zero Graphite. The provisional correction hides `cc-target-field`; rollback restores the Custom selection and numerical values but leaves its target input hidden. Reproduced with extracted shipped functions. This is a **pre-existing rollback defect**, newly exercised by this rejection.

The remaining checks:

- **Numerical rollback works.** An extracted-function caller harness with mocked backend/UI confirmed restoration of peak values, `_backendParams`, `fitResult`, provenance, `nextId`, manual anchors, charge inputs, ROI/background inputs, and the original `ccShift`. Separately, the existing `pushUndo()` still adds a history entry and clears Redo; rollback does not reverse those history changes.
- **Threshold:** I found no credible resolved Graphite anchor rejected at one millionth of the strongest component within this bounded model. However, the reproduced near-zero escape makes the threshold insufficient as the sole support check.
- **Whole-operation rejection is appropriate.** Auto-Fit promises model plus charge correction. Keeping the fit requires explicitly transforming it out of the provisional frame and explaining the partial outcome. Restoring the previous state with the red notice is coherent.
- **Amber warning remains unchanged**, after successful application only.
- **Locks and links do not cause ordinary misfires:** Auto-Fit replaces the old model with fresh, unlinked peaks and explicitly sets `fixAmplitude: false`.
- **No other automatic fitted-centre-to-global-charge path found.** Other charge writers handle manual inputs, restoration, or propagation of an existing shift. The charge-reference checkbox only marks a peak.

All nine committed tests pass; they miss the all-components-near-zero case.

**VERDICT: NO-GO.**
