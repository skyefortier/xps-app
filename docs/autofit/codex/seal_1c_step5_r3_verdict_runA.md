**NO-GO: the round-2 production fixes are present, but activating a frozen seal-only result still throws. One MAJOR finding and remaining MINOR test gaps; no BLOCKER found.**

**MAJOR — Tab activation cannot display a seal-only result.** `activateTab` sees the absent legacy `rFactor` and assigns `_computeRFactor(...)` into the result. Class methods run in strict mode, so a frozen `{seal}` throws `TypeError: Cannot add property rFactor, object is not extensible`. Activation stops before repainting the history panel, Results, sidebar and chart. See [index.html:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3325) and [index.html:3330](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3330).

An in-memory harness executing the extracted class method reproduced this for **CURRENT, PENDING and UNCONFIRMED**, with zero downstream renders. STALE avoids the assignment. This is the frozen result shape required by [plan:231](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/docs/superpowers/plans/2026-10-14-seal-1c-page.md:231) and already used by [_seal_only:524](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:524). No loader implementation is needed to reproduce it. Gate the legacy lazy computation off for sealed results; the display reader already supplies recorded R.

**1. Round-2 findings, both runs**

| Finding | Round-3 status |
|---|---|
| **MAJOR:** stack state exists only in hidden labels | **Resolved.** The visible legend includes `_stackSourceStateText`, including the unconfirmed reason and stale cause; verdict handling refreshes it. [index.html:2559](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:2559), [index.html:12018](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12018), [index.html:9267](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9267) |
| **MAJOR:** stale seal-only CSV/XLSX formats an absent statistic | **Resolved.** The stale branch never reads/formats χ². Extracted-function checks confirmed both exports complete with warning/state and live-model rows. [index.html:14421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14421) |
| **MINOR:** engine card reads `backendResult` | **Resolved.** Sealed visibility uses the designation’s engine. [index.html:10844](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10844) |
| **MINOR:** open history misses a verdict after switching tabs | **Repaint logic resolved.** Activation rebinds the panel; any verdict refreshes the active tab’s list. Seal-only activation still encounters the separate MAJOR above. [index.html:3330](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3330), [index.html:9261](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9261) |
| **MINOR:** tests do not discriminate their claims | **Partially resolved.** Visible legend, missing-statistic exports, engine-card and already-open-preview cases now discriminate their original defects. Remaining gaps are listed in answer 4. |

The detached verification change is also correct for the reviewed cache behavior: both gates use `_cachedVerdict`. A focused check confirmed that an old-numerics answer triggers verification and the resulting current-numerics answer is reused. [index.html:9237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9237)

**2. Switch ON: does every §7 consumer satisfy the contract?**

**Not end to end**, because seal-only activation aborts rendering. Apart from that failure, the reviewed consumer bodies select the intended sources:

| Consumers | Assessment |
|---|---|
| Chart and stack | Recorded arrays while displayable; existing preview paths when stale. Stack build/update share envelope selection and refresh labels. [index.html:12290](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12290), [index.html:11768](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11768), [index.html:11999](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11999) |
| Results, sidebar, Quantify, Auto-Fit area warning | Shared recorded model/area readers; corresponding denominators use those areas. Results and Quantify carry state text. [index.html:8056](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8056), [index.html:10857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10857), [index.html:10965](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10965), [index.html:7900](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:7900) |
| Header, R, uncertainties | Recorded statistics, sigma, bounds and initial values; stale suppression; pending/unconfirmed R has no level wording. Activation’s legacy R write remains defective. [index.html:10173](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10173), [index.html:14579](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14579), [index.html:14672](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14672) |
| History, alternatives, certificate notice | History judges its own record; previews use its arrays. Alternatives remain previewable while adoption independently requires CURRENT. [index.html:17086](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:17086), [index.html:12447](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12447), [index.html:9825](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9825), [index.html:9667](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9667) |
| CSV/XLSX, TSV, PNG | Recorded values while displayable; stale warnings and statistic/sigma suppression. The stale seal-only table-export failure is fixed. [index.html:14404](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14404), [index.html:13934](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13934), [index.html:13978](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13978) |
| Designation, `.fit.json`, Batch summary | Designation and fit-file metadata use the sealed readers; Batch’s returned statistic comes from local O. [index.html:10065](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10065), [index.html:13057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13057), [index.html:10656](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10656) |

Serializers/loaders remain outside this step’s review.

**3. Switch OFF**

**No regression found for existing valid results.** Sealed readers return through their legacy branches; history activation/verdict repaint changes are gated. The area/model readers also passed isolated OFF checks without page state. [index.html:9308](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9308), [index.html:9374](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9374), [index.html:9397](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9397)

Literal equivalence has one small exception: CSV/XLSX now substitutes `—` for a missing/non-finite non-stale statistic instead of the previous formatting behavior, even while OFF. This is not a demonstrated regression for valid fit results. [index.html:14421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14421)

**4. Do the tests each fail on their named defect?**

**No — MINOR coverage gaps remain.**

- The new legend, stale-export, engine-card and open-preview assertions target the earlier defects directly. [test:427](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:427), [test:531](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:531), [test:553](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:553), [test:564](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:564)
- The tab-switch test enters an **unfitted** B; the seal-only test invokes `renderResults` directly. Neither catches activation of a frozen sealed result. [test:558](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:558), [test:582](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:582)
- “Undo” still reverses a parameter assignment rather than invoking undo. “Sigma and bounds” changes bounds only. [test:98](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:98), [test:261](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:261)
- XLSX now checks result cells, but its stale test does **not** assert absence of the statistic row. Adding a statistic alongside its warning would pass. [test:517](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:517), [test:547](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:547)
- PNG tests still capture metadata, not drawn curves or annotation text. Several numerical tests retain agreeing legacy duplicates, so they do not establish independence from those fields. [test:349](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:349), [test:198](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:198), [test:360](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:360)

Validation: **199/200 selected JavaScript tests passed**. The Python-backed parity test and Chromium startup were blocked by temporary-directory permissions. Focused in-memory checks confirmed the activation failure and the export/cache repairs. No files changed.

**VERDICT: NO-GO.**
