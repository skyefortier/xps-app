No BLOCKER found. Two MAJOR findings remain.

1. **MAJOR — Background and ROI edits leave old evidence actionable and saveable.** [templates/index.html:4502](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:4502)  
   Disposition 2’s invalidation is not connected to these controls: background edits call `_invalidateBgCache()`, which only clears `bgIntensity`; ROI inputs only call `updatePlot()`. Reproduced both paths retaining `_currentAlternative(0)` and persisted counts. Change the background window or ROI after fitting: the old comparison still permits adoption under the new settings. History restore also reinstates matching peaks/evidence without restoring the background/ROI used for that evidence. Bind validity to the fit context and cover its actual edit/restore paths.

2. **MAJOR — An in-flight edit can receive a falsely matching evidence key.** [templates/index.html:7482](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7482)  
   The acceptance guard checks tab ownership, but not intervening model changes. Reproduced with the real extracted request builder, `runFit`, and result application: request centre **285 eV**; change and lock the live centre at **290 eV** while awaiting the response; returned centre **285.4 eV** is skipped because of the new lock. The code then stamps the 290-eV model with a fresh key, and `_startsIfCurrent()` accepts the mismatched evidence. Capture and validate the originating model/context before applying the response.

3. **MINOR — An already-active alternative preview survives invalidation.** [templates/index.html:7325](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7325), [templates/index.html:9054](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:9054)  
   Reproduced: preview an alternative, then edit a centre. Evidence is cleared, but `_historyPreview` remains and the chart draws it without checking validity. Clicking Preview again refuses the stale action before reaching toggle-off. An ordinary subsequent Run Fit also retains the overlay. Clear alternative previews on invalidation/result replacement, or validate their source when drawing.

4. **MINOR — Renaming a peak deletes counts and choice provenance.** [templates/index.html:5786](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:5786)  
   The actual name input calls `updatePeakParam()`, which unconditionally calls `_invalidateFittedY()`. Reproduced both `starts` and `chosenAlternative` becoming null after a rename. The cosmetic-edit test directly assigns fields, bypassing this handler. Preserve evidence for cosmetic edits.

5. **MINOR — Tooltip still exceeds the counts-only requirement.** [templates/index.html:7194](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7194)  
   When starts agree, it still says “the data pin it down from those starts.” Optimizer agreement does not establish that interpretation. This Round 1 finding remains unchanged.

6. **MINOR — CSV/XLSX still omit the recorded adoption.** [templates/index.html:10818](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:10818)  
   After successful adoption, both exports include only the starts summary and never inspect `chosenAlternative`. The saved choice therefore disappears from exported tables. This is separate from the accepted `.fit.json` import disposition.

The suspected linked-parent request issue does **not** reproduce in the normal adoption path: `getPeak()` only checks parent existence, and adoption preserves IDs. I found no alternative-modified field omitted from the server’s parameter response. The key does omit `_afAsymMin`/`_afAsymMax`, although I found no ordinary UI edit path changing those bounds alone.

Validation: **64 focused JavaScript tests and 18 Python tests passed**, plus extracted-function reproductions above. Six API cases were excluded because their fixtures require filesystem writes. No files changed.

**VERDICT: NO-GO**
