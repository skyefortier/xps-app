# Background math implementation round 4 — run A (commit b03344c; codex exec, reasoning high)

1. **MAJOR — Linear certifies an impossible background.** [templates/index.html:4839](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4839), [fitting.py:2009](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2009).  
   With `E=[3,2,1,1,0]`, `I=[20,25,10,30,5]`, and both background bounds set to `1`, the window contains anchors `(1,10)` and `(1,30)`. No affine function passes through both. Nevertheless, the page marks `[10,10,10,10,10]` converged, and the throwing producer returns it. I also reproduced a **successful server fit** against that curve. The existing flat fallback remains outside the statement check.

2. **MAJOR — Incomplete raw data bypasses restored-fit certification.** [templates/index.html:9580](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9580).  
   The guard returns success when `rawBE.length < 2`. Take the old Shirley fit on `E=[3,2,1,0]`, `I=[13,10,3,2]`, with background `[13,9.07142857,3.57142857,2]`, and truncate its raw arrays to `[3]` / `[13]` while retaining the frozen fit arrays. Restoration accepts it; the extracted plotting code emits the rejected curve as its Background dataset. Its original certificate residual is **14.3% of the span**. The spectrum loader also retains this malformed record without warning. Missing data needed for certification must cause rejection.

3. **MAJOR — Spectrum loading drops valid ascending-order fits.** [templates/index.html:11251](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11251).  
   `createTab` sorts raw data descending, but the loader copies `roiBE` and `background` unchanged. A current linear spectrum file with `E=[0,1,2,3,4,5]`, `I=[10,12,40,30,22,20]`, and certified background `[10,12,14,16,18,20]` is consequently dropped as “fitted on other points.” This can occur when saving a spectrum from an ascending project. I reproduced rejection for **all eight methods**, including cases with a blank ROI bound, an interior background window, averaging 3, and a charge shift; corresponding descending records survive.

Verification: **73 Python and 53 JS focused tests passed**, including numerical and certificate parity. All four measurement summaries and the **3 restored / 62 different / 56 missing** census reproduced exactly; the documented owner consequence is accurate. All **376 Smart/Smart-experimental pairs** were bit-identical. HTTP/browser suites were not rerun under the read-only restrictions; lifecycle reproductions used extracted page functions. No files changed.

**VERDICT: NO-GO.**
