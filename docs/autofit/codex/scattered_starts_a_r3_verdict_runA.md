No BLOCKER or MAJOR found. Both Round 2 MAJORs are resolved. Two MINOR findings remain:

1. **MINOR — Already-visible counts do not refresh after background/ROI edits.** [templates/index.html:7290](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7290)  
   Keep Results open and change endpoint averaging or ROI. Those handlers call `updatePlot()`, which never refreshes Results; the old counts/table remain instead of the stale notice until Results is reopened. Adoption, preview requests and saves correctly reject the stale evidence.

2. **MINOR — Alternative-preview cleanup still has gaps.** [templates/index.html:7231](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7231)  
   Preview an alternative, then toggle a peak lock: the real `toggleLock()` changes the key without triggering cleanup or redraw, leaving the overlay visible. Also, replacing the result with one having identical fitted parameters/context preserves the old preview—even when the replacement has no alternatives. Reproduced both with extracted functions. Refresh on lock changes and bind previews to result identity, or clear them unconditionally after successful fitting.

I agree that changing the method selector may preserve historical evidence. I found no additional missing request setting or automatic tab/load normalization that invalidates fresh evidence.

Read-only validation: **75 focused JavaScript tests and 18 Python tests passed**; six filesystem-writing API cases excluded. No files changed.

**VERDICT: GO**
