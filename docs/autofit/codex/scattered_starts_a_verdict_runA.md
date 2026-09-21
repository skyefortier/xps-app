The site table misses `_invalidateFittedY`, parameter/lock edits, and the `.fit.json` import branch in `TabManager.fromJSON`. These expose stale evidence and lost provenance.

No BLOCKER-level mutation of the server’s primary fit was found. The following MAJOR findings prevent GO.

1. **MAJOR — Clustering merges different chemical assignments.** [fitting.py:1253](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/fitting.py:1253)  
   Reproduced: GL “C-O” at 286 eV/60% and GL “C=O” at 287.5 eV/40% compare equal after those assignments swap. Consequently, a start can count toward “same solution” despite reversing the named fractions; a lower-χ²ᵣ swapped solution can disappear entirely. Compare components by stable ID. Permit permutations only within explicitly interchangeable groups with matching chemistry and constraints; identical lineshape is insufficient.

2. **MAJOR — Edited models still accept stale alternatives.** [templates/index.html:7261](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7261)  
   `_altPeaks` checks only IDs and component count. Reproduced: change C-O’s shape from GL to DS and its centre to 290 eV; the old alternative remains applicable, producing a DS component with parameters and displayed χ²ᵣ taken from the GL fit. Lock, linkage, background and ROI changes have similar exposure. `_invalidateFittedY` leaves `starts` intact. Bind the evidence and actions to the fitted model/settings, and invalidate or explicitly label them after changes. This also applies after undo: preserving the existing `fitResult` behaviour must not make its counts describe the restored model.

3. **MAJOR — Failed adoption leaves new parameters paired with the old result.** [templates/index.html:7311](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7311)  
   Reproduced with the actual `runFit` function returning `success:false`: C-O changed from 286.41 to 286.71 eV, the old `fitResult` survived, and the notification falsely said “Previous peaks and result kept.” No choice was recorded. Switching tabs during the refit likewise preserves the already-written alternative on the originating tab while discarding its result. Adoption needs an owner-bound transaction with explicit success/failure handling and rollback. Successful local fallback also currently drops the choice provenance.

4. **MAJOR — Tab switching can disable the required check.** [templates/index.html:7375](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7375)  
   `peakSpecs` is captured before upload, but `n_starts` reads `state.peaks` afterward. Reproduced a request containing three peaks with `n_starts: 0`. Scenario: start on multi-component tab A, switch to single-component B during upload, then return to A before the fit completes. A accepts a result without the required check. Capture eligibility alongside `peakSpecs`.

5. **MAJOR — The summary confuses solution count with start count.** [templates/index.html:7216](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7216)  
   Reproduced: all three starts reach one lower-χ²ᵣ alternative, yet the summary says “0 of 3 … reached this solution; **one start** found a DIFFERENT solution.” CSV/XLSX repeat this error. `_startsForSave` preserves the number of alternative clusters but loses their total start count. Sum `alternative.n_starts`, persist that count, and distinguish starts from solutions.

6. **MINOR — Scatter changes sign and exceeds its documented perturbation range.** [fitting.py:1206](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/fitting.py:1206)  
   Reproduced: amplitude −100 with an open lower bound becomes positive; FWHM 0.1 within `[0.1,15]` becomes exactly 0.845 across sampled starts; centre 1 within `[0,100]` becomes exactly 5. These remain inside bounds, but violate amplitude ×/÷3, width ×/÷1.5 and centre ±0.5. Preserve amplitude sign and clamp those perturbations to the actual bounds; reserve the middle-90% redraw for shape parameters.

7. **MINOR — Choice provenance disappears from exports and fit-file round trips.** [templates/index.html:10762](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:10762), [templates/index.html:3408](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:3408)  
   After successful adoption, CSV/XLSX never inspect `chosenAlternative`. Separately, save → load → re-save `.fit.json` drops both counts and choice: import clears `fitResult` and preserves only local-engine provenance. Preserve the source metadata without presenting an imported model as a newly fitted result.

8. **MINOR — Alternative previews leave misleading history state.** [templates/index.html:7287](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7287)  
   Preview a history snapshot, then an alternative: the overlay changes, but the snapshot’s `hist-preview-active` highlight remains. An alternative preview also survives an ordinary subsequent Run Fit; `'alt:0'` identifies no particular result. Clear history highlighting when replacing the preview and invalidate alternative previews when their source result changes.

9. **MINOR — Tooltip exceeds the counts-only wording.** [templates/index.html:7190](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7190)  
   When all starts agree, “the data pin it down” attributes optimizer agreement to data determination. Replace it with the observed count or “all sampled starts reached the same solution.”

Validation: **54 focused JS tests and 16 Python tests passed**; six upload/API cases were excluded for read-only execution. Additional probes reproduced findings 1–6 and verified byte-identical Nelder output. Inspection found no primary-result aliasing path: lmfit deep-copies parameters, the first two seed streams remain unchanged, and global methods skip the check.

Important missing tests are integrated adoption failure/tab-switch/undo, same-ID model edits, multiple starts per alternative cluster, preview lifecycle, and provenance round trips. Summary-only spectrum/project records render safely; no-check exports omit the line. Native `confirm()` matches existing conventions, and the named confirmation correctly uses strict `> 1 eV`.

**VERDICT: NO-GO**
