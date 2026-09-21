No BLOCKER found. Two findings remain.

1. **MAJOR — Sidebar refresh can conceal stale Results and Quantify.** [templates/index.html:7354](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7354) uses sidebar badges as the sole record of rendered suppression. `addPeak` redraws that sidebar before `updatePlot` performs the comparison. With Results or Quantify open, place another peak: the previous unsupported verdict becomes stale and its badge disappears, but Results retains its suppressed row and Quantify retains its exclusion. Reproduced with extracted production functions; both panels’ HTML remained unchanged. Lock All has the same ordering gap, though switching panels subsequently repairs it. Refreshing the sidebar must not mask stale consumers.

2. **MINOR — Lock toggles leave stale chart designations.** [templates/index.html:7347](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7347) repaints the chart only when removing an alternative preview. Without a preview, toggle an unsupported component’s lock: the sidebar and tables refresh, but its chart dataset still says “not supported by the data.” Reproduced: `_isUnsupported` returned false, with zero chart repaints.

Auto-Fit rollback restores the original support objects. Explicit null keys and an absent `_startsLiveKey` safely return false; no remaining bare array-callback misuse found.

Validation: **144 JS tests passed**, including all 21 support tests. One Python-backed parity test and Python collection were blocked by read-only temporary-directory restrictions. No files changed.

**VERDICT: NO-GO.**
