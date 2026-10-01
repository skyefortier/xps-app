# Background math implementation round 4 — run B (commit b03344c; codex exec, reasoning high)

1. **MAJOR — Short raw-data records bypass restoration checks.** [templates/index.html:9580](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9580).  
   A truncated project with `rawBE:[0]`, `rawIntensity:[2]`, but a retained four-point fit and background `[2,3.57142857,9.07142857,13]` is accepted without checking that curve. I reproduced the project loader retaining it without a warning. `updatePlot` then selects the stored background despite the live computation reporting “fewer than two data points.” That curve fails Shirley’s statement on its original data by **14.3% of the span**. Both project formats share this bypass. Missing or insufficient raw data must reject the restored fit.

2. **MAJOR — Spectrum loading drops valid ascending-order fits.** [templates/index.html:11251](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11251), with sorting at [3159](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:3159).  
   Load an ascending project, fit it, save a spectrum, then reload that `.spec.json`. `createTab` sorts raw data descending, while the loader copies `roiBE` and `background` unchanged. Restoration consequently rejects the current fit as “fitted on other points.” Using the actual loader and `createTab`, I reproduced rejection for **all eight methods**; corresponding descending files survive. Preserve the saved order or reorder all associated fit arrays consistently.

Verification: **73 Python and 55 JS checks passed**, including background/certificate parity and manual interpolation. **512 project round trips** passed. All four measurement summaries and **376 Smart/Smart-experimental comparisons** reproduced. The census matches exactly—**3 restored, 62 differing, 56 without curves**—and its owner-decision consequence is now accurately stated.

Lifecycle reproductions used extracted page code in memory. One HTTP test was blocked by the read-only temporary-directory restriction; browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
