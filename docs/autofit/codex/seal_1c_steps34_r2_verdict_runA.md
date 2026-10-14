**NO-GO for steps 3–4 as complete.** The main numerical and ownership fixes are sound, but the staged-check cache handoff remains incomplete. I found one MAJOR issue and three MINOR issues/coverage gaps. No files changed.

1. **Round-1 findings, both runs**

| Finding | Round-2 status |
|---|---|
| Signed-zero / undefined-field transport identity | Original cases resolved; sparse-array defect remains below. [_jsonEqual, index.html:8858](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8858) |
| Auto-Fit producer continuity and anchor identity | Resolved. [index.html:8952](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8952) |
| Binding memo ignores in-place sample edits | Resolved for element assignments; deleting an element escapes the new comparison. [index.html:8932](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8932) |
| Rejection hides Auto-Fit mismatch / reports UNCONFIRMED prematurely | Resolved within an installed-seal attempt. [index.html:9068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9068) |
| Missing staged transaction ownership | Ownership guards added; transfer of answers into the final seal remains incomplete. [index.html:9094](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9094) |
| Cached numerical verdict prevents explicit retry | Resolved after completion; retry during an outstanding attempt still does nothing. [index.html:9151](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9151) |
| Supersession test never installs the newer operation; missing tab switch | Resolved: the test now claims both operations and separately switches tabs. [test_browser_seal_step4.py:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:158) |
| Missing negative and producer tests | Substantially addressed, but some tests do not isolate their named defect; see answer 6. |
| JSON-stringified identity assertions conceal differences | Resolved for the strict comparisons in step 3. [test_browser_seal_step3.py:23](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step3.py:23) |

Run B’s observation that the switch is unused remains true, but producer activation is expressly deferred to step 7. That alone is not a finding against this review’s scope. [Plan:350](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/docs/superpowers/plans/2026-10-14-seal-1c-page.md:350)

2. **Record rule: correct for ordinary dense records, with a MINOR hole**

The intended equivalences are correct: `-0` equals `0`, undefined object fields equal absent fields, undefined array entries equal null, and NaN remains unequal to null. Keeping `_sameModel` strict is right: implementation identity and JSON-record equivalence are different contracts. Bindings now use `_sameRecordModel`. [index.html:7093](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:7093)

**MINOR:** `_jsonEqual` uses `x.every`, which skips array holes. I reproduced:

```text
_jsonEqual(Array(1), [7]) → true
_jsonEqual([7], Array(1)) → false
```

Their JSON records are `[null]` and `[7]`: genuinely different records compare equal, and equality is asymmetric. Iterate every index, including holes. [index.html:8863](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8863)

The memo’s `same` helper has the same hole-skipping problem: `delete rawIntensity[i]` preserves length and can reuse the previous successful binding. Ordinary value assignment is correctly detected. [index.html:8932](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8932)

3. **Auto-Fit evidence: resolved**

The final and anchor producer contexts must now match, and `require_component` must identify the anchor selected from the recorded starting model. Request reconstruction separately binds that requirement to each request. A final request dropping or changing the anchor requirement no longer binds. [index.html:8952](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8952), [index.html:8986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8986)

The honest producer uses the same anchor selection and passes the same `anchorId` to the final request, so I found no new honest-Auto-Fit refusal from these checks. [index.html:8585](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8585), [index.html:8653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8653)

This remains acceptance **as recorded**; the server expressly does not prove `required`. [fitting.py:3296](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/fitting.py:3296)

4. **Verification precedence and staged transactions**

Installed-seal aggregation now follows the requested precedence. A mismatch resolves immediately; unreachable or unconfirmed cannot decide while another check remains outstanding. Attachment also checks attempt, owner, seal, operation and active-tab identity. [index.html:9068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9068), [index.html:9129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9129)

**MAJOR — staged answers do not survive normal seal construction.** `_verifyStagedCheck` records the original R/O references, while `_makeSeal` deep-clones them. `_commitStaged` then searches exclusively by reference identity. I reproduced both staged checks returning consistent, followed by `_makeSeal(...)` and `_commitStaged(...)`: commit returned `true`, but the seal had **no cached verdict**. It falls back to another verification instead of entering the two completed answers as §9 requires. [index.html:7127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:7127), [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9102), [index.html:9114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9114)

Provide an explicit handoff preserving the verified immutable records’ identity into the final seal. Deferring producer integration does not resolve this mismatch between the two existing APIs.

The staged owner/operation/transaction guards themselves reject superseded replies correctly. [index.html:9099](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9099)

**MINOR — “check again” is not always a new attempt.** The outstanding-attempt return runs before checking `retry`. I reproduced zero new requests and a null return from `_ensureVerified(owner, true)` while an attempt was pending. A stalled attempt therefore cannot be superseded through this API. [index.html:9155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9155)

5. **Switch-off behaviour**

I found no ordinary-input behavioural or numerical regression. The fix does not activate verification in shipped producer flows. Replaying the local engines against `70e1097` produced **121 bit-identical results, zero differences, zero skipped**, with artifact writes suppressed.

6. **Test strength**

The corrected ownership tests, mixed-outcome tests, signed-zero sample test, in-place assignment test, and actual Use-solution/Batch production tests meaningfully cover the original defects.

**MINOR — several remaining tests can pass despite their named defect:**

- The staged success test creates **and installs** the final seal before checking its R/O objects. It bypasses the pre-seal-to-final-seal handoff that loses cached answers. [test_browser_seal_step4.py:445](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:445)
- The held-value test also changes `fixFwhm` without updating `paramMap`; inventory rejection satisfies its assertion even if the held-value projection check is absent. Lock/link cases similarly allow earlier inventory rejection. [test_browser_seal_step4.py:282](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:282)
- “Always starts a new attempt” only tests completed attempts. [test_browser_seal_step4.py:228](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:228)
- The outstanding-check test covers consistent and mismatch partners, but omits **unreachable plus outstanding**, the original premature-state case. [test_browser_seal_step4.py:403](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:403)

Validation: **144 focused JS tests passed**; one Python-backed test and the browser suite were blocked by read-only temporary-directory restrictions. The counterexamples above ran against extracted current-page functions.

**VERDICT: NO-GO.**
