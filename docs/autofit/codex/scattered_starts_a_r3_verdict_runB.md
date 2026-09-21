No BLOCKER or MAJOR found. Both Round 2 MAJORs are resolved. Two MINOR preview issues remain:

1. **MINOR — Lock changes leave an open alternative preview visible.** [templates/index.html:5789](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:5789)  
   Preview an alternative, open Peaks, then lock a centre. The real `toggleLock` changes the key but triggers no repaint, so `_dropStaleAltPreview()` never runs. Reproduced: evidence is stale, but the overlay remains. Adoption and saves correctly reject the stale evidence. Refresh the preview after lock changes, including Lock All.

2. **MINOR — The preview key identifies the model, not its originating result.** [templates/index.html:7233](/Users/skyefortier/xps-app/.claude/worktrees/feature-scattered-starts-check/templates/index.html:7233)  
   If another successful fit returns identical peak fields/context, its key matches the previous result. The success-path cleanup therefore preserves the old alternative overlay even if the new result has no alternatives. Reproduced with extracted functions and a replacement result. Clear alternative previews unconditionally on successful result replacement, or bind them to result identity.

I agree that changing the method selector may preserve evidence describing the completed fit. I found no additional missing numerical request field or routine tab/reload normalization that falsely invalidates it. Additional extracted-`runFit` probes correctly discarded in-flight background, endpoint-averaging and ROI edits.

Validation: **75 JavaScript tests and 18 Python tests passed**; six Python cases requiring filesystem writes were excluded. No files changed.

**VERDICT: GO**
