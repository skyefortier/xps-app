No BLOCKER found. Two MAJOR issues remain.

1. **MAJOR — Background/ROI edits leave stale alternatives actionable.** [templates/index.html:4497](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:4497)  
   Background controls call `_invalidateBgCache()`, which only clears `bgIntensity`; ROI controls call `updatePlot()`. Neither calls `_invalidateFittedY()`. Change background type, endpoint averaging, or ROI after fitting: the peak key remains identical, so old comparisons can still be previewed, adopted, saved and exported. Reproduced: background invalidation left evidence current, adoption proceeded, and saved counts remained `3`. History restore also reinstates the old peak key without restoring its background/ROI, bypassing even explicit evidence clearing. Bind evidence to the complete fitting context and check that context on restore.

2. **MAJOR — Edits during adoption can receive a fresh key despite mismatching the server result.** [templates/index.html:7460](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7460)  
   Acceptance checks tab identity only. The spinner covers the chart; peak controls remain editable. Start adoption, change a centre to 290 eV and lock it while waiting. The server returns 286.7 eV; `applyBackendResult` honours the new lock, leaving 290 eV, and line 7482 stamps that mismatched model with a fresh `startsModelKey`. Reproduced using the actual `runFit` and parameter applier: evidence was accepted as current and the choice recorded. Capture the original live model/context before awaiting and reject completion if either changed.

3. **MINOR — An already-open alternative preview survives invalidation and subsequent fits.** [templates/index.html:7328](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7328)  
   Preview an alternative, then edit a parameter: `starts` becomes null, but `_historyPreview` survives and `updatePlot` continues drawing it without checking its source. Ordinary Run Fit also leaves it installed. The identifier `alt:0` does not identify a particular result. Clear alternative previews when their evidence changes, and bind them to the source result.

4. **MINOR — Actual edit handlers contradict the cosmetic exemption and stale-notice behavior.** [templates/index.html:5786](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:5786)  
   Renaming a peak through `updatePeakParam` unconditionally calls `_invalidateFittedY()`, deleting both counts and choice provenance. Reproduced with the extracted handler. Parameter edits likewise delete `starts`, so `_startsPanelHtml` returns nothing instead of the promised stale notice. The tests mutate objects directly and miss these handler effects. Preserve evidence for cosmetic changes and retain enough metadata to show the intended stale notice.

5. **MINOR — The model key omits two request fields.** [templates/index.html:7204](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7204)  
   `peakToBackendSpec` reads `_afAsymMin` and `_afAsymMax`; neither appears in `_STARTS_MODEL_FIELDS`. Probe: changing `_afAsymMax` from `0.5` to `0.8` changed the request bound while `_startsIfCurrent` still accepted the evidence. Include both fields. I found no routine rendering mutation that would invalidate every fresh key.

6. **MINOR — The tooltip still exceeds counts-only wording.** [templates/index.html:7194](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7194)  
   “The data pin it down from those starts” remains unchanged from round 1. Optimizer agreement does not establish data determination; report the observed agreement only.

7. **MINOR — CSV/XLSX still omit adoption provenance.** [templates/index.html:10818](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:10818)  
   Accept an alternative and export: both formats include the new comparison summary but never inspect `chosenAlternative`, losing the recorded selection. This is separate from the accepted `.fit.json` import behavior.

The linked-parent lookup only checks existence; it does not copy live parent parameters into the alternative request. I found no additional missing server-returned parameter in normal, unedited adoption. Tab switching carries peaks and results together.

Read-only validation: **64 focused JavaScript tests passed; 18 Python cases passed, with six API/upload cases deselected**, plus the behavioral probes above.

**VERDICT: NO-GO**
