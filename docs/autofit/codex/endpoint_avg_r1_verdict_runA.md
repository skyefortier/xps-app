# Endpoint averaging refusal — Codex round 1, run A (commit 64c3376)

Seven **MAJOR** findings. The range refusal is incomplete; several readers still bypass it.

1. **MAJOR — Editing the field can leave an invalid averaging marked as fitted.**  
   [_fitKeyCanon](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:8419) still canonicalizes averaging with `parseInt`. Consequently, `1` and `1e2` compare equal. I reproduced changing `1 → 1e2` during upload: Run Fit applied the response, announced “Fit complete,” and stored `1e2` in `startsModelKey`. The same equality governs current statistics, alternative previews, exports/saves, the local fallback’s edit check, and Auto-Fit’s response checks. Its post-charge-shift background check adds no averaging validation.  
   **Non-physical inputs: no**—ordinary data and a number-field edit suffice.

2. **MAJOR — Restored fits and stack reconstruction accept invalid averaging.**  
   [_computeBackgroundForSource](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:10011) feeds saved settings into the unchecked background reader. I exercised the actual restoration functions with `ui.endpointAvg` equal to `"0"`, `"51"`, and `"1e21"`: each returned no failure and remained non-stale. These records can therefore be displayed and saved as fitted despite Run Fit refusing their settings. Stack reconstruction uses the same producer.  
   **Non-physical inputs: no**—previously accepted saved fits suffice.

3. **MAJOR — Direct autofit and parity entry points bypass the validator.**  
   [fit_candidate](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/engine.py:900) calls `_compute_background` without `check_endpoint_avg`; [background_like_run_fit](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/parity.py:75) also lacks the check. On a normal positive C 1s spectrum, `fit_candidate` returned **converged fits at `0`, `51`, and `1e21`**. Parity computed backgrounds for all three. Method-wrapper validation does not protect direct engine callers.  
   **Non-physical inputs: no**—ordinary spectra and explicitly supported script entry points. A shared one-line refusal can protect these paths.

4. **MAJOR — The Python saved-project reader still clamps and disagrees on valid values.**  
   [ReferenceFit.endpoint_avg](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/reference.py:256) maps `0` and negative values to `1` before `run_fit` can refuse them. It also reads saved `"3.0"` as **1**, while the page reads **3**. Thus the plan’s assertion that an out-of-range saved value reaches `run_fit` and is refused is false for the lower bound.  
   **Non-physical inputs: no**—`"3.0"` suffices. The additional 5,001-digit spelling of 3 also becomes 1 in Python; that synthetic variant should be logged under the owner’s rule.

5. **MAJOR — Batch Fit refuses after destructive model changes, and blank bypasses refusal.**  
   The [new Batch check](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:13951) executes after `_pushUndoFor`, replacing target peaks/settings/charge correction, and clearing its previous fit. A source value of `51` therefore changes an already-fitted target before refusing. The summary names the correct target, but the refusal is not atomic. Separately, `_captureUI` converts a blank field to `"1"` before propagation, so Batch can fit a blank value that Run Fit refuses.  
   **Non-physical inputs: no.**

6. **MAJOR — Archived Find Peaks validates the coerced value instead of the field.**  
   [runFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:17600) still applies `parseInt(field) || 1` before validation. Executing that request-building code produced `0 → 1`, `1e2 → 1`, and `2.5 → 2`, without refusal. The server receives an apparently valid value, so its validator cannot catch the discrepancy.  
   **Non-physical inputs: no**—requires invoking the archived path, expressly included in this review.

7. **MAJOR — The Auto-Fit behavioral test does not prove its new claim.**  
   In [fit_start_poll.test.js](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/fit_start_poll.test.js:315), `findGraphiteRawBE` always returns `null`, and the assertion accepts either the averaging message **or** “No strong peak found.” I removed Auto-Fit’s averaging refusal in memory: **the test still passed**. The separate structural assertion detects deletion, but does not repair this behavioral proof. The Run Fit test also claims “before the spinner” while its spinner stub records nothing.  
   **Non-physical inputs: not applicable**—these are test defects.

Compatibility checks: numeric `1`, `3`, `50`, JSON `3.0`, and NumPy integer inputs passed. The page helper accepts `"3.0"`, `"+3"`, `" 7 "`, hex `"0x10"`, and long leading-zero strings consistently with its background reader. Blank, `"1e1"`, and API string `"3"` are newly refused by design; these are additional acceptance changes beyond a numerical range check. I found no changed background arithmetic for accepted ordinary numeric values.

Validation: **98 focused JavaScript tests and 24 Python tests passed**. In-memory session probes confirmed plain 400 refusals through `/api/fit`, `/api/fit/start`, `/api/background`, and `/api/analyze`’s least-squares path. Browser tests were not run under the read-only restrictions. Harness defaults changed from blank to `"1"` reasonably; the reproducibility test’s replacement values still exercise quarter-window saturation. No files changed.

**VERDICT: NO-GO**
