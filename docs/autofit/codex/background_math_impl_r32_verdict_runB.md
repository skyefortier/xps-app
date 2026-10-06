# Background math implementation — Codex round 32, run B (commit 94d59c3)

Reviewed `94d59c3`, read-only. **One new MAJOR finding.**

## PROPORTIONALITY RULING

1. **Yes, for the concrete failures reported in rounds 25–31.** All terminate in refusal rather than incorrect numbers or false current status. I would reclassify none of those demonstrated cases as (a) or (b).
2. **Yes, another input can falsely restore as current.** The RMSE agreement test accepts `Infinity <= Infinity` after intermediate overflow. The concrete case below carries a valid fit key, so the keyless-fit policy does not prevent it.
3. **The new finding blocks deployment under this round’s criteria.** Logged round-31 B remains **MINOR, category (c), non-blocking** for its demonstrated refusal. It does not justify NO-GO by itself.

**1. MAJOR — RMSE overflow certifies an inconsistent record as current. Categories (a) and (b); deploy-blocking.**  
[templates/index.html:10160](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10160)

Concrete Spectrum-file reproducer:

- Energies: `[280, 280.5, 281, 281.5, 282]`.
- Gaussian: center `281`, FWHM `1`, amplitude `1000`; background None.
- Stored envelope and `fitCounts`: `[62.5, 500, 1000, 500, 62.5]`.
- Stored RMSE and reduced χ²: `0`; `uploadFull: true`; matching `startsModelKey`.
- Replace only `rawIntensity` with `[1e200, 1e200, 1e200, 1e200, 1e200]`.

The counts pass rejects this inconsistency, but the [RMSE-only fallback](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10327) retries. Squared residuals overflow; `rc`, `sums`, and `tolOwn` become infinity. Consequently, `Math.abs(rc - fr.rmse) <= tolOwn` returns true. The search’s upper squared-error bound also overflows, so its prunes do not stop acceptance.

Executing the production loader, status accessor, Results renderer and CSV exporter with UI stubs produced:

- Status **`current`**, with no stale/refusal notice.
- Displayed RMSE **`0.0`**, although the mathematical RMSE is approximately **`1e200`**.
- Exported reduced χ² **`0.0000`**, without a warning.

This is a synthetic, inconsistent saved record—not a demonstrated ordinary instrument-data round trip. It nevertheless satisfies the explicitly requested “any input” scope. Non-finite intermediate arithmetic must not establish agreement.

Verification: census reproduces **0 current / 81 stale / 40 peaks-only**; Python twin verdicts agree. All five measurement summaries and student-note figures reproduce. All **202** upload inputs, seeds, background arrays and net areas match committed records. **144 JS and 83 Python tests passed**; two Python fixtures were filesystem-blocked. The narrowed scattered-starts test checks actual draws and passes. **5,000** additional comparisons found no discrepancy against disabled numerical pruning/memoization. CI floor is **569**. Full optimizer/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
