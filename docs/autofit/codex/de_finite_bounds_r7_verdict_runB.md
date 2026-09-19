Reviewed HEAD `f49ad4a`, read-only. **41 tests passed; the upload test was excluded.** No files changed.

- **BLOCKER:** None found.

- **MAJOR — Exact zero-signal fits now fail.** [fitting.py:1060](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1060)  
  Reproducer: `x=linspace(999,1001,101)`, counts uniformly `1000`, manual background uniformly `1000`. One Gaussian with fixed centre `1000`, fixed FWHM `0.5`, amplitude start `1`, requested amplitude minimum `0`, open maximum; NumPy seed `4`.

  DE converges at amplitude `0`, χ² `1.01e-248`. Successful refinement moves amplitude to `1e-10`, giving χ² `1.88173e-22`. Because **P=0**, HEAD rejects it and reports failure caused by generated limits. Reproduces with `n_perturb=0` and `3`; **the round 6 parent succeeds**. Near-zero negative data and a noise-free Gaussian of amplitude `1e-12` also fail. The new allowance removes the protection against absolute numerical displacement at the amplitude bound.

- **MINOR — The claimed 1% deterioration rejection is not general.** [fitting.py:1060](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1060)  
  Using the same reported-χ² fault-injection approach as the committed test, a 1% worse refinement is accepted for a Poisson spectrum with 1,000 points and counts `975546–992346`: DE χ² `922.278867`, injected refinement `931.501656`, allowed increase `9.860053`.

  This also reproduces with normalized data and weights `1`: χ² `0.000954056` → `0.000963597`, with `P=971.998153`. These are acceptance-rule counterexamples; I did not observe the real solver spontaneously producing that deterioration.

- **MINOR — P includes channels omitted because their energy is NaN.** [fitting.py:1059](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1059)  
  On a 101-channel normalized Gaussian, make one energy NaN with intensity `1e6` and weight `0.001`. Both solvers omit that residual (`ndata=100`), but its contribution inflates P from `7.528059` to `1000007.528059`. A fault-injected refinement χ² `0.005` is then accepted over DE χ² `9.21003e-5`; physically removing the omitted channel correctly rejects it. Ordinary NaNs in `y_sub` are excluded correctly. P needs the same effective observation mask as the objective.

**VERDICT: NO-GO.**
