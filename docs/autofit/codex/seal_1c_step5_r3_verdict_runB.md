**NO-GO: one MAJOR seal-only failure remains. No BLOCKER found.** The four concrete round-2 implementation defects are fixed; test coverage is only partially repaired.

**1. Round-2 findings, both runs**

| Finding | Status |
|---|---|
| **MAJOR:** Stack state exists only in hidden dataset labels | **Resolved.** State text now reaches the custom legend’s `.name` element, and verdicts refresh that legend. [index.html:2581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:2581), [index.html:12018](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12018), [index.html:9269](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9269) |
| **MAJOR:** Stale seal-only CSV/XLSX formats a missing statistic | **Resolved.** STALE bypasses statistic formatting; output selects warning rows. [index.html:14421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14421), [index.html:14459](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14459) |
| **MINOR:** Engine card depends on legacy `backendResult` | **Resolved.** A readable seal’s designation controls the card. [index.html:10844](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10844) |
| **MINOR:** Open history misses verdicts after switching tabs | **Resolved for ordinary activation.** Activation rebinds the list to the active tab; any verdict refreshes an open list. The seal-only activation failure below remains a separate problem. [index.html:3330](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3330), [index.html:9263](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9263) |
| **MINOR:** Tests do not discriminate their stated defects | **Partially resolved.** Visible-legend, seal-only export/card, preview timing and XLSX-cell assertions improve coverage. Remaining gaps are listed in answer 4. |

The detached verifier now consults `_cachedVerdict` both before requesting and before accepting an answer. An extracted-function check confirmed that an obsolete cached answer permits recomputation, while the replacement answer prevents another request. [index.html:9237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9237)

**2. Switch ON: not every consumer works with a seal-only result.**

**MAJOR — Activating a tab containing a frozen `{seal}` result throws before rendering finishes.** `activateTab` sees the absent legacy `rFactor`, calls `_computeRFactor`, then assigns its return value to the frozen result. Class methods execute in strict mode, so this throws:

```text
TypeError: Cannot add property rFactor, object is not extensible
```

I reproduced this using the extracted `activateTab` method and `_computeRFactor`, with the state judgment stubbed to CURRENT, PENDING and UNCONFIRMED. All three failed before `renderResults`; STALE bypassed the assignment. The offending assignment is at [index.html:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3325); the legacy calculator returns `null` without `fr.be` at [index.html:14550](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14550).

This uses exactly the frozen seal-only shape already introduced by the test helper. Those tests install it on the active tab and never reactivate that tab. [test_browser_seal_step5.py:524](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:524)

The sealed activation path must avoid that legacy cache write and obtain R from the view. No loader implementation is needed to expose or fix this failure.

Otherwise, the reviewed §7 consumer migrations are consistent:

- **Chart and stack:** recorded arrays while displayable, existing preview branches otherwise; stack state is now visible. [index.html:12290](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12290), [index.html:11768](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11768)
- **Results, sidebar, Quantify and area warning:** shared record/model/area/support readers; I found no additional mixed area denominator. [index.html:9376](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9376), [index.html:10857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10857), [index.html:10965](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10965)
- **Statistics, uncertainties and evidence:** state-qualified presentation, recorded parameters/bounds/start values, and independent CURRENT enforcement for adoption. [index.html:10173](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10173), [index.html:14672](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14672), [index.html:9824](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9824)
- **History:** snapshot-record judgment and recorded preview arrays remain appropriate. [index.html:17085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:17085), [index.html:12447](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12447)
- **Exports, designation, `.fit.json`, Batch:** no further migration defect found in the reviewed branches. [index.html:13933](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13933), [index.html:13980](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13980), [index.html:13057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13057), [index.html:10656](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10656)

Serializers/loaders remain outside this step.

**3. Switch OFF**

**No behavioral regression found for today’s supported result shapes.** The readers retain their early OFF gates, including the previously problematic area/model readers. [index.html:9377](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9377), [index.html:9397](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9397)

This is a qualified review conclusion, not exhaustive browser-equivalence proof.

**4. Do the tests each fail on the defect they name?**

**No — remaining MINOR coverage gaps:**

- The “undo” test reverses an assignment rather than invoking undo. [test:98](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:98)
- The uncertainty test discriminates **bounds**, but does not independently discriminate the sigma source. [test:257](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:257)
- PNG assertions inspect metadata, not the plotted curves or visible annotation. [test:388](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:388)
- The stale XLSX test checks warning/state rows but never asserts absence of the statistic row. [test:544](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:544)
- The already-open preview test checks its changed label, not replacement of its recorded curve. [test:577](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:577)
- The tab-switch test activates an empty tab; it does not return to a frozen seal-only result, so it misses the MAJOR failure. [test:582](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:582)

By inspection, the new legend, stale-export exception and engine-card assertions do discriminate their original defects.

Validation: **186/187 selected JavaScript tests passed**; the remaining Python-backed test required a writable temporary directory. Browser tests failed during Chromium setup because temporary-directory creation was denied. Review and focused reproductions were read-only; no files changed.

**VERDICT: NO-GO**
