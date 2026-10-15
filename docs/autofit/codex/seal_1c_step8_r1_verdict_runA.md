**NO-GO. One MAJOR and three MINOR findings; no BLOCKER found.**

1. **Presentation: incomplete.**

   **MAJOR — PNG exports omit LEGACY state when the fit has no record.** The new qualifier remains inside `_isFitRecord(_rec0)`. Without a record, `rec` is null and the original PNG is downloaded without state metadata. All 121 committed legacy fits lack a record. I reproduced both branches: record-bearing legacy fits receive the chunk; recordless fits do not. Emit state metadata independently of record availability. [templates/index.html:14809](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:14809)

   **MINOR — legacy fallback wording does not cover the whole matrix.** A stale legacy fit bypasses the new header suffix and tooltip, showing only “background changed” or “model changed.” Legacy fits dropped to PEAKS-ONLY have `fitResult = null` and return before the new Results note; without provenance, they show only “Run the fit to see results.” [templates/index.html:10526](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:10526), [templates/index.html:11132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:11132)

   Otherwise, the touched CURRENT/PENDING/UNCONFIRMED acceptance wording reads recorded evidence, and STALE suppresses it. The R panel preserves pending/unconfirmed qualification without level wording. I found no newly added “as recorded” label attached to recomputed values, and no visible promotion of a legacy fit to confirmed CURRENT. [templates/index.html:9620](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:9620), [templates/index.html:10069](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:10069), [templates/index.html:15048](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:15048)

2. **Saves and append-only exports: no step-8 save regression found.**

   Project, spectrum and `.fit.json` legacy serialization remain unchanged. In particular, `.fit.json` still calls `_exportSealState`, which returns nothing for legacy fits; `_exportFitState` is confined to exports. [templates/index.html:13467](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:13467), [templates/index.html:13480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:13480), [templates/index.html:13690](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:13690)

   CSV/TSV additions remain after existing content; XLSX additions remain after existing Info rows. No existing data lines, rows or columns are changed by this step. The PNG defect above is missing metadata, not a prefix violation. [templates/index.html:9944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:9944), [templates/index.html:14939](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/templates/index.html:14939)

3. **Measurements: numerical comparison reproduced; one reported statistic is wrong.**

   I located the named seal-1b inputs outside this checkout, verified all three hashes, and reran the JS generator entirely in memory against `ef750f6`. Its output exactly matches `release_measure.json`. The same reply feeds both readings, and the main-side parameter application, χ² and RMSE calculations match main’s behavior. R substitutes the recorded background, explicitly relying on 1b’s background-parity evidence. [scripts/seal_1c_release_measure.js:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/scripts/seal_1c_release_measure.js:49)

   **MINOR — the median seal sizes are incorrect.** Across the output’s 121 seals, the medians are **68,123 B raw / 26,293 B gzipped**, not approximately 90 KB / 35 KB. The maxima, project totals, ×2.73 ratio and 111 CURRENT / 10 UNCONFIRMED counts match. All ten unconfirmed tabs contain LA components. [docs/findings/seal-1c/README.md:70](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/docs/findings/seal-1c/README.md:70)

   The size script measures committed files versus freshly refitted saves, as documented—not isolated seal overhead on otherwise identical saves. The 0.59% χ² median is across all 202 targets; among the 113 affected targets it is approximately 1.02%. [scripts/seal_1c_save_size.py:70](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/scripts/seal_1c_save_size.py:70), [scripts/seal_1c_release_measure.js:90](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/scripts/seal_1c_release_measure.js:90)

4. **Tests: useful assertions, incomplete guarantees.**

   **MINOR — “saves are untouched” is not actually tested.** That test checks only absence of three strings, covers project and `.fit.json` but not spectrum saves, and would pass after unrelated saved fields were altered or removed. Compare parsed saved fields against the baseline. [tests/test_browser_seal_step8.py:106](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/test_browser_seal_step8.py:106)

   Other gaps explain the missed defects: export coverage is CSV/TSV only; the stale-legacy test does not assert its collected statistics state or inspect the header; certificate wording and pending/unconfirmed acceptance wording are untested. [tests/test_browser_seal_step8.py:54](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/test_browser_seal_step8.py:54), [tests/test_browser_seal_step8.py:131](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s8/tests/test_browser_seal_step8.py:131)

   The changed JS expectations retain their exact comparisons or anchored patterns; they do **not** weaken assertions. Reading production constants into the harness does not replace the independent expected strings.

Validation: 154 selected JS tests passed; one backend-parity test failed because the read-only sandbox provides no writable temporary directory. Browser tests were not run. No files changed.

**VERDICT: NO-GO.**
