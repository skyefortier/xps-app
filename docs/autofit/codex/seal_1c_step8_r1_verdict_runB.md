Found **one MAJOR and two MINOR findings; no BLOCKER**.

1. **Presentation: not fully compliant.**

   **MAJOR — Recordless legacy PNG exports omit their state entirely.** The PNG code adds `sealState` only when `_isFitRecord(_rec0)` succeeds; otherwise it downloads the original, unannotated blob. This affects the committed legacy fits, which predate fit records. I reproduced that branch directly. Add state metadata independently of whether a fit record exists. [templates/index.html:14809](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:14809)

   **MINOR — Legacy qualification misses fallback presentations.** A legacy fit restored stale takes the header’s stale branch, bypassing both the new suffix and tooltip qualification. Its Results note is correct. Legacy fits dropped to PEAKS-ONLY receive generic no-fit presentation and no legacy export state because `_isLegacyFit(null)` is false. These do not satisfy every cell of §5’s grouped LEGACY/PEAKS-ONLY presentation. [templates/index.html:10526](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:10526), [templates/index.html:11132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:11132), [templates/index.html:9705](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:9705)

   Otherwise, CURRENT/PENDING/UNCONFIRMED receive the acceptance qualification only while displaying the recorded fit; STALE suppresses it. The starts and certificate notices use the same recorded-display gate. I found no touched surface falsely labelling live recomputation “as recorded,” or explicitly labelling a legacy result CURRENT. [templates/index.html:9621](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:9621), [templates/index.html:10015](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:10015), [templates/index.html:10064](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:10064), [templates/index.html:11208](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:11208)

2. **Saves and export layout: no step-8 save regression found.**

   Project, spectrum and `.fit.json` legacy serialization remain unchanged. `_exportFitState` is confined to export paths; saves retain `_exportSealState`. CSV/TSV data and XLSX’s existing rows and columns remain in place, with the state added in the trailing block. The PNG defect is missing metadata, not displaced content. [templates/index.html:9939](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:9939), [templates/index.html:13467](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:13467), [templates/index.html:14940](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:14940)

3. **Measurements: numerical comparison sound; one reported statistic is wrong.**

   I verified the three input hashes and reproduced `release_measure.json` exactly, including 202 distinct targets. I also recomputed backgrounds using main’s implementation: **328/328 bit-identical**, validating the script’s substitution of `O.background_y`. The χ² counts and differences, RMSE, R, component curves and areas support the findings. [scripts/seal_1c_release_measure.js:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/scripts/seal_1c_release_measure.js:49), [release_measure.json:3](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/docs/findings/seal-1c/release_measure.json:3)

   **MINOR — The reported seal-size medians are incorrect.** Across the 121 output entries, the medians are **68,123 B raw and 26,293 B gzipped**, not approximately 90 KB and 35 KB. The totals, ×2.73 ratio, maxima and **111 CURRENT / 10 UNCONFIRMED** split match; all ten corresponding committed models contain LACX. The size ratio measures the documented fresh-refit/resave workflow, rather than isolated seal overhead. [README.md:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/docs/findings/seal-1c/README.md:69), [scripts/seal_1c_save_size.py:74](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/scripts/seal_1c_save_size.py:74)

4. **Tests: useful assertions, but incomplete coverage; no weakened JS assertions.**

   The new tests detect missing CURRENT acceptance/starts wording and the exercised legacy qualifiers. They do **not** cover PNG/XLSX qualification, certificate wording, PENDING/UNCONFIRMED wording, or the stale legacy header. The save test checks only forbidden strings and seal absence, omits spectrum saves, and cannot establish unchanged serialized fields. [tests/test_browser_seal_step8.py:54](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/test_browser_seal_step8.py:54), [tests/test_browser_seal_step8.py:106](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/test_browser_seal_step8.py:106)

   The JS changes preserve exact comparisons and the anchored local-fit regex; they add the required legacy text without relaxing previous checks. [fit_acceptance.test.js:340](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/js/fit_acceptance.test.js:340), [local_lm_descent.test.js:174](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/js/local_lm_descent.test.js:174), [stale_statistics.test.js:184](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/js/stale_statistics.test.js:184)

Validation: 125 selected JS tests passed; one Python-backed parity test was blocked by the read-only environment’s unavailable writable temporary directory. Browser tests were inspected, not executed. No files changed.

**VERDICT: NO-GO.**
