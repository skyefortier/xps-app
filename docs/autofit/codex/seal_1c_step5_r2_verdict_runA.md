**Step 5 is still NO-GO. Two MAJOR issues remain; no BLOCKER found.** Review was read-only.

1. **MAJOR — Stack state text is still invisible.** `_stackEnvLabel` now includes “confirming”, “unconfirmed”, or “no longer applies”, but Chart.js has `legend.display: false` and its tooltip accepts only `:raw` datasets. The visible custom legend still shows only the source name and local designation. Thus the new envelope labels do not resolve round 1’s missing visible source state. Verdict repainting also does not refresh that custom legend. See [index.html:11967](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11967), [index.html:12018](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12018), [index.html:2559](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:2559), and [index.html:9228](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9228).

2. **MAJOR — STALE CSV/XLSX exports still require a legacy statistic.** `exportFitTable` unconditionally executes `_shownStats(...).chiReduced.toFixed(4)`. For STALE, `_shownStats` falls back to `fr.chiReduced`; a `{seal}` result has no such field. Both exports throw before producing their warning and live-model rows. I reproduced both exceptions with the extracted functions. The stale branch must avoid formatting a statistic it will not report. See [index.html:14372](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14372) and [index.html:9312](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9312).

3. **MINOR — Results retains a legacy engine-card gate.** The “lmfit” card depends on `backendResult`, rather than the seal’s designation. Removing legacy duplicates from a valid sealed server result therefore removes its engine card. See [index.html:10805](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10805).

4. **MINOR — Several test claims remain broader than their assertions**, detailed below.

**1. Round-1 findings, both runs**

| Finding | Round-2 status |
|---|---|
| Stack update reconstructs the subtracted envelope | **Resolved.** Build and update share `_stackEnvY`, which selects recorded `fittedSub`. [index.html:11959](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11959) |
| Stack retains invalidated support labels | **Resolved.** In-place updates now refresh component labels. [index.html:12155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12155) |
| Stack lacks visible source-state text | **Unresolved**, MAJOR finding 1. |
| History bypasses state and ownership | **Resolved for record presentation.** Rows and previews use `_snapshotSealState`, including spectrum bindings and verification. [index.html:17102](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:17102) |
| History does not repaint after verification | **Resolved for the owning tab’s open list and preview.** [index.html:9225](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9225) |
| Server `.fit.json` imports as local | **Resolved.** Server exports write `objective: null`, consistent with the unchanged classifier/importer. [index.html:13012](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13012) |
| STALE TSV/PNG lose the failed check or misidentify it as an edit | **Resolved.** TSV includes state/check/reason; PNG distinguishes failure from editing and includes the state in its metadata. [index.html:13865](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13865), [index.html:14153](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14153), [index.html:14291](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14291) |
| `_componentArea` / `_shownPeak` touch page state before OFF gate | **Resolved.** Both return before reading `state`; confirmed in an isolated harness without page state. [index.html:9344](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9344), [index.html:9367](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9367) |
| Header gates on legacy `chiReduced` | **Resolved.** The sealed branch checks the displayed statistic and handles STALE separately. [index.html:10137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10137) |
| `.fit.json` reads legacy choice/reportability | **Resolved.** It uses `_chosenOf` and the designation. [index.html:13018](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13018) |
| Batch summary reads the independently calculated statistic | **Resolved at its source.** The returned `outcome.chiReduced` now comes from local O when sealed. [index.html:10618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10618) |
| Tests do not discriminate adequately | **Partially resolved.** Stronger stack, history, import and OFF tests were added; important gaps remain. |

**2. Does every §7 consumer satisfy the ON contract?**

**No**, because of the findings above. The principal numerical migrations otherwise look consistent:

- Main chart reads recorded components, background, envelopes and residuals. [index.html:12261](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12261)
- Results/sidebar, Quantify and the Auto-Fit area warning use the shared area/model readers. I found no separate live-percentage denominator mixed with recorded areas. [index.html:10820](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10820), [index.html:8049](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8049), [index.html:7898](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:7898)
- Header/R, uncertainty rules, alternatives and certificate notices use recorded values and state gates. [index.html:14529](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14529), [index.html:14624](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14624), [index.html:9786](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9786)
- Stack arithmetic, history, TSV, PNG, designation, `.fit.json` choice/reportability and Batch’s statistic are migrated as described above.
- CSV/XLSX correctly select recorded rows while displayable, but fail the STALE/no-duplicates case.
- Serializers/loaders remain step 6; their unfinished migration is not counted against this review.

**3. Is record-only history judgment right, and is detached verification sound?**

**Yes for an explicitly “as recorded” history display.** It should remain possible to inspect a valid earlier fit after editing today’s model. `_snapshotSealState` still checks the record against the owning spectrum; it bypasses only the live-model comparison. The preview then draws that record’s own grid and envelope. This does **not** establish that restoring the snapshot into today’s context would be CURRENT. See [index.html:9246](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9246) and [index.html:12398](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12398).

I found no blocking flaw in the detached path: it deduplicates by seal, checks owner liveness before accepting a result, caches numerical answers without claiming a fit operation, and triggers repaint. Extracted-function checks confirmed deduplication, cache reuse, mismatch repaint and rejection after owner closure. [index.html:9200](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9200)

**4. Is switch-OFF behavior exactly today’s?**

**No behavioral regression found in the reviewed paths.** The two premature state accesses are fixed. The local engine’s unconditional return-value change selects the same `chiReduced` copied into O during construction, so it introduces no numerical difference while OFF. [index.html:10596](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10596)

That is a qualified review conclusion, not full browser-equivalence proof: browser execution was blocked.

**5. Does each test fail on its named defect?**

**No.** Improvements are real, but the suite does not establish that claim:

- The new stack test discriminates envelope reconstruction and stale dataset labels, but checks `ds.label`, not visible state. It passes despite MAJOR finding 1. [test_browser_seal_step5.py:407](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:407)
- The XLSX test named “state and provenance” asserts only a PENDING state row. Deleting provenance output would not fail it; it also never checks exported result cells. [test_browser_seal_step5.py:499](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:499)
- STALE export coverage checks TSV and PNG metadata, leaving CSV/XLSX without legacy fields untested. PNG drawing/annotation remains unasserted. [test_browser_seal_step5.py:484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:484)
- Panel tests now assert sidebar percentages and R wording, but ordinary fixtures retain matching legacy statistics. They do not discriminate the remaining engine-card gate or prove independence from duplicate fields. Initial panel rendering is also manual. [test_browser_seal_step5.py:171](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:171)
- History tests now discriminate edited-live-model handling, failed records and offline state. The failed-record test starts its preview **after** verification, so it does not test an already-visible preview changing on the verdict. [test_browser_seal_step5.py:437](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:437)
- The OFF disagreement test and server/local import tests directly discriminate their targeted regressions. [test_browser_seal_step5.py:152](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:152), [test_browser_seal_step5.py:468](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:468)

Validation: **186/187 selected JavaScript tests passed**. The remaining Python-backed test required a writable temporary directory. Browser tests could not start Chromium because its temporary-directory creation was denied. Focused read-only harnesses reproduced both MAJOR findings.

**VERDICT: NO-GO.**
