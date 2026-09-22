- **MAJOR — Differential Evolution silently skips the check.** [fitting.py:1375](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1375) calls `model_without.fit` directly, bypassing the finite-box/refinement machinery. Reproduced with ordinary open amplitude bounds: the full fit succeeds, but `required` becomes `{ran:false, reason:"error"}` with “requires finite bound for all varying parameters.” Auto-Fit consequently proceeds without testing redundancy. Reuse the candidate machinery for the reduced model.

- **MAJOR — Linked parameters can disable the check.** [fitting.py:1740](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1740) removes only direct dependants; [fitting.py:1374](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1374) reconstructs expressions sequentially. Two reproduced failures, both with successful full fits:
  - Remove peak 1 with links `3 → 1`, `4 → 3`: peak 4 survives and references deleted parameters.
  - Remove unrelated peak 2, with retained child 4 ordered before parent 3: expression insertion fails before parent parameters exist.
  
  Both return `ran:false` with `NameError: p3_amplitude`. Remove dependants transitively and construct retained parameters before assigning expressions.

- **MAJOR — The requested anchor can belong to another tab.** [templates/index.html:7262](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/templates/index.html:7262) reads live `state.peaks` **after** awaiting upload; `peakSpecs` was captured before it. An extracted-function probe sent Graphite ID 1 in the model but `require_component:"2"` after switching tabs during upload. If the user returns before the response, the ownership check passes and Auto-Fit uses another component’s verdict. Capture the anchor ID alongside `peakSpecs`, before the await.

- **MINOR — Exact redundant components are reported required because of numerical residue.** [fitting.py:1387](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1387). Reproduced with one exact pseudo-Voigt line represented by two identical half-amplitude components. Removing either is mathematically lossless, yet least-squares reports `required:true`, F ≈ 1,035 (`χ²_with ≈ 3.86e−28`, `χ²_without ≈ 1.16e−26`); LM reports F ≈ 1.56e11. The zero-only special case does not handle near-exact fits.

- **MINOR — Stochastic refits lose their seed.** [fitting.py:1749](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1749) passes unseeded `kws`. Instrumentation confirmed basinhopping received seed `2015001725` for the full fit and no seed for the refit, despite an explicit caller seed. This loses controlled reproducibility for the acceptance check.

Five Python tests and all three new JavaScript tests passed; the upload/API test was excluded under read-only constraints.

The gate ordering and rollback wiring look correct. `required` remains backend-result metadata, which can persist with that result; it does not become a peak parameter. Ordinary Run Fit returns `required:null`, and the LM unchanged-result test passes. The stated `p`/`dof` definitions are implemented. Starting from fitted values is a valid comparison, but the single refit does not rerun `n_perturb` and cannot establish that another basin would not absorb the anchor.

**VERDICT: NO-GO.**
