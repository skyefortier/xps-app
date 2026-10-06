# Background math implementation — Codex round 32, run A (commit 94d59c3)

Reviewed `94d59c3`, read-only.

## PROPORTIONALITY RULING

1. **I agree with category (c) for the documented round 25–31 findings.** Their concrete reproducers lose a fit through refusal; none demonstrates wrong output or false-current status. Under this round’s rules, they are non-blocking.
2. **Yes, another input can restore wrong statistics as current.** The finite-input overflow case below defeats RMSE agreement despite having a matching fit key and exactly one reading.
3. **The new finding blocks deploy: categories (a) and (b).** Logged round-31 B remains **MINOR, category (c), non-blocking** for its demonstrated refusal.

**New finding**

1. **MAJOR — RMSE overflow accepts a contradictory record as current. Categories (a), (b).** [templates/index.html:10162](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10162), [search window:10190](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10190).

   Concrete spectrum-file input:

   - Raw and fitted energies: `[280,281,282]`.
   - Raw counts and `fitCounts`: `[1e200,1e200,1e200]`.
   - Background None; zero-amplitude Gaussian, center `281`, FWHM `1`.
   - Background and fitted envelope: `[0,0,0]`.
   - Stored RMSE `1`, `uploadFull: true`, and matching `startsModelKey`.

   All supplied numbers are finite. Squaring the residuals overflows, making `rc`, the summation allowance, and `tolOwn` infinite. Agreement becomes **`Infinity <= Infinity`**, which passes. The search’s squared upper bound also overflows, so pruning does not prevent acceptance.

   Executing the production spectrum loader retains the fit, emits only its normal loaded message, and returns **`_statsRecordState === 'current'` with RMSE `1`**. The actual RMSE is **`1e200`**; Results therefore reports a wrong number as current.

   This is a hand-constructed, extreme-scale record, not a demonstrated backend-generated fit. It nevertheless meets this round’s explicit “any input” criterion. An in-memory finite-value guard makes the same loader refuse it. Use overflow-safe RMS arithmetic or refuse non-finite agreement calculations.

Verification: census and Python twin reproduce **0 current / 81 stale / 40 peaks-only**. All five measurement summaries and student-note figures reproduce; all **202** upload round trips, seeds, background arrays, and net areas match. **90 targeted JS checks and 82 Python checks passed**; two HTTP fixtures were filesystem-blocked. The narrowed scattered-starts test checks actual draws and passes. Full suites were not completed. No files changed.

**VERDICT: NO-GO**
