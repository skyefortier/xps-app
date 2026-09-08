# Codex adversarial review — Find Peaks endpoint averaging (feature-find-peaks-endpoint-avg) — round 2, RUN A (2026-09-08, reviewed at 7d37cea / code 2b10c58)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 77,499.
Prompt: docs/autofit/codex/find_peaks_endpoint_avg_r2_review_prompt.txt
Evidence CORRECTION (both runs caught it): the round-2 prompt claimed the combined browser files passed; the author's chained run had logged '1 failed, 14 passed' behind a tail -1 (tests/test_browser_find_peaks_progress.py::test_progress_indicator_shows_spinner_timer_and_real_readout_then_clears — 'elapsed timer never ticked upward', also the single failure in the round-1 full suite: 1 failed / 794 passed / 7 skipped, gate 3 passed). Isolation re-runs and the disposition are in the round-3 prompt. Chains now print failures and abort on them.
Round 2: A GO / B NO-GO — validation and AST guard CLOSED (both); B MINOR: 1e21 passes both validators, _fpLast records '1e+21' and the preview's parseInt reads 1 while the engine caps at window//4 — fixed in round 3 with a shared upper bound (50, the panel's max); both: evidence discrepancy.

**Findings**

1. **MAJOR — resolved: validation.** `pop_endpoint_avg` rejects strings, booleans, containers, nonpositive values, fractions, and non-finite floats before conversion. All four Find Peaks methods use it. Frontend validation precedes upload and records the validated value. Advanced JSON accepts `3.0`; JavaScript serializes it as `3`. Synchronous analyze returns validation errors as HTTP 400; asynchronous analyze reports them through job status.

2. **MINOR — resolved: structural guard.** The package-wide AST scan handles both attribute calls and nested functions. I independently verified all 17 discovered calls pass a nonconstant `endpoint_avg`. The behavioural spy checks actual stability-refit background recomputations at 7.

3. **MINOR — existing, outside scope: alternate entry points.** Direct Python engine calls bypass the helper. Manual `/api/fit` and `/api/background` retain coercion and uncaught-infinity risks, but neither bypasses validation in the Find Peaks request path. No new round-2 arithmetic or wiring defect found; default-1 arithmetic remains unchanged.

4. **MINOR — unresolved evidence discrepancy.** Logs confirm **35 wiring/seam tests passed**, but the combined browser run reports **1 failed, 14 passed**, contradicting the supplied green summary. Output was truncated with `tail -1`, hiding the failure identity. I independently passed eight focused Node tests; the full Node rerun encountered sandbox temporary-directory failures. Current-commit full pytest/parity completion remains unverified.

Code review supports GO; the browser evidence needs correction. Actual HEAD is `7d37cea`, with only the round-2 prompt added after `2b10c58`. Archived verdict files were not read.

VERDICT: GO
