# Background math implementation round 3 — run B (commit 056a3ce; codex exec, reasoning high)

1. **MAJOR — Spectrum loading drops valid fits saved by this version.** [templates/index.html:11212](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11212).  
   `_loadSpectrumFile` does not copy `data.roiBE` or `data.background` into `fr.be` / `fr.bgIntensity` before calling the new check. Consequently, **Run Fit → Save Spectrum → reload** drops every non-manual/non-`none` fit, including linear, claiming its background was not saved—even though it is present in the file. Reproduced through the actual loader. Manual fits escape rejection but also lose their stored background; a subsequent stack reconstruction substitutes Shirley.

2. **MAJOR — Restoration selects different ROI points and rejects current project fits.** [templates/index.html:9537](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9537).  
   `getROIData` honors either ROI bound independently; `_recordBackground` filters only when **both** are finite. With `E=[5,4,3,2,1,0]`, `I=[20,22,30,40,12,10]`, blank `roiMin`, `roiMax=4`, Shirley and background bounds `[1,4]`, the current certified fit uses `[4,3,2,1,0]`. Restoration selects all six points and drops it as fitted on different points. This affects both project formats. The descending-only reconstruction also rejects ascending saved records with an interior ROI.

3. **MINOR — The stated owner-decision consequence is false on committed files.** [plan:103](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:103).  
   Running the actual restore function over the committed projects keeps **3 of the 65 fits carrying stored curves**: `Cl2p Scan`, `Cl2p Scan_0`, and `Cl2p Scan_1` in `Cl2p_projfit_test.proj.zip`. Their curves match the certified curves after six-significant-figure rounding. The report conflates failing the strict certificate with failing the implemented restoration rule. “No older saved fit is restored” needs correction.

4. **MINOR — The tightened guard still accepts consumption without refusal.** [tests/js/background_not_converged.test.js:89](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/tests/js/background_not_converged.test.js:89).  
   This in-memory mutation passes the actual guard:
   ```js
   const bg = computeBackground(be, inten);
   const failure = _bgFailure(bg);
   return bg.map(v => v + 1);
   ```
   Assigning a failure reason does not establish refusal. An unreachable inline check, `if (false) _bgFailure(computeBackground(...))`, also exempts a later unchecked consumer.

Validation: **73 Python and 50 JS checks passed**, including background/certificate parity and manual interpolation. All four measurement summaries reproduced exactly; 36 ordinary current-project round-trip cases passed. HTTP/browser validation remained limited by the read-only environment. No files changed.

**VERDICT: NO-GO.**
