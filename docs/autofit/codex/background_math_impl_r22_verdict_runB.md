# Background math implementation — Codex round 22, run B (commit 423f2d1)

Reviewed `423f2d1`, read-only. **Five MAJOR findings and one MINOR:**

1. **MAJOR — The 64-candidate cutoff discards uniquely identifiable fits.** [templates/index.html:10160](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10160)  
   The cutoff runs before stored-count filtering. Reproducer: 100 samples, `E[i]=280+0.1i`, `I[i]=1+0.00001i`; a keyless legacy fit on the first five samples, manual background `1`, zero-amplitude Gaussian, envelope `1`, RMSE `0`, and project-rounded background/subtracted counts. More than 64 offsets meet the RMSE allowance, but the stored counts identify **only indices 0–4**. Production restoration drops it as indistinguishable. Removing only the cutoff restores it without background staleness.

2. **MAJOR — The energy allowance hides genuine background changes.** [templates/index.html:10012](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10012)  
   Reproducer: keyless legacy Gaussian, center `285`, FWHM `1`, amplitude `100000`, background `1000`, energies `280…290` in `0.1` steps. Apply charge correction `+0.1`; change manual anchors to add an **8-count triangular bump** centered at corrected energy `285.3`, returning to baseline at `285.1` and `285.5`. Restoration accepts the background and installs the edited curve; disabling the allowance correctly reports **0.79365% stale**. The original upload energies are exactly reconstructible here.

   The allowance is not bounded relative to background height. For a Gaussian its maximum is approximately `1.428 × amplitude/FWHM × 1e-4` counts—**1.43% of this realistic example’s background**, exceeding the intended 0.1% tolerance.

3. **MAJOR — Older local-engine spectra falsely reload stale.** [templates/index.html:9994](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9994)  
   Missing `uploadFull` is treated as proof of rounded server-upload energies, including `engine: 'local'`. Local fitting used full-precision browser energies. A successful local Gaussian fit on `280.00004 + 0.1i`, center `280.5`, FWHM `0.2`, amplitude `1000`, constant manual background `100`, saved as an older spectrum, reloads **0.276514% background-stale** despite no change.

4. **MAJOR — The RMSE bound remains invalid under cancellation.** [templates/index.html:10125](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10125)  
   Concrete extreme but accepted input: eight energies `280…287`, counts `0.1`, manual background `−1e15`, locked Gaussian amplitude `1e15`, center `283.5`, FWHM `1e16`. The backend succeeds: its envelope is `0`, and residuals `(I−B)−M` are `0.125`. Restoration computes `I−envelope = 0.1`; the **0.025 discrepancy exceeds the approximately 0.005 bound**, dropping the sole correct reading. Bounding arithmetic using only `|I|+|envelope|` misses the large cancelling background/component terms.

5. **MAJOR — Save Spectrum still mixes legacy fitted and current component grids.** [templates/index.html:11520](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11520)  
   Restore a legacy Gaussian fitted at four-decimal upload energies from raw `280.00004 + 0.1i`, center `280.5`, FWHM `0.2`, amplitude `1000`; change manual background from `10` to `20`. Restore correctly marks it stale. The production spectrum saver then writes, at `280.40004`, **envelope ≈510, background 10, component 500.277280**. `_asFitted` preserves Voigt mixing, but components are still evaluated at different energies from the preserved envelope.

6. **MINOR — The student-note generator crashes.** [scripts/bg_math_preview_vs_fitted.py:16](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/scripts/bg_math_preview_vs_fitted.py:16)  
   `fit_grid()` now returns four values; this caller unpacks three. Correcting that unpacking in memory reproduces the note’s rounded numbers.

Verification: census **10/71/40** reproduced exactly; Python twin verdicts agree on all 121. The allowance applies to **16/81**, maximum **0.588712%**, as reported. Measurement analysis reproduced exactly; all **202 upload inputs, seeds, and background arrays** match the committed records. The narrowed test still compares actual draws; CI floor is **552**.

**120 targeted JS and 115 Python checks passed.** Four Python fixtures required forbidden writes; the remaining Python run was stopped for budget. Full suites were not verified clean. No files changed.

**VERDICT: NO-GO.**
