One **MAJOR** loader defect and one **MINOR** test-discrimination finding remain. Reviewed `seal-1c-s5..6ab526e`; no files changed.

**1. Round-2 findings, covering both runs**

| Finding | Status |
|---|---|
| Hostile engine/ID values throw during seal installation | **Resolved.** Types are checked before coercion, and the schema wrapper catches exceptions. Extracted-function probes confirmed rejection without throwing. [index.html:7163](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7163), [index.html:7252](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7252) |
| Model parameter types unchecked | **Resolved for the reported reader hazards.** Centre, width and amplitude require numbers; name/shape require text; fit fields require scalars. [index.html:7252](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7252) |
| Component `params: {}` accepted | **Resolved.** An own `area` property is required and typed. [index.html:7278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7278) |
| Background-effect contents unchecked | **Reported payloads resolved; replacement validator has a new MAJOR failure below.** Exact-form checks cover server and local O. [index.html:7292](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7292), [index.html:7300](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7300) |
| Legacy certificates/effects crash Results | **Reported renderer failures resolved.** Certificates are typed; `_fitRecordRows` contains formatting exceptions. However, legacy validation can now throw before rendering. [index.html:12058](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:12058), [index.html:9906](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9906) |
| `SETTLE` masks loader-triggered inactive-tab verification | **Resolved in the ZIP regression.** It uses passive `WAIT`, then requires every tab CURRENT. [test_browser_seal_step6.py:115](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:115) |
| Auto-Fit does not count/challenge both checks | **Resolved.** Interception precedes loading; assertions require two requests, inclusion of E, and STALE when E fails. [test_browser_seal_step6.py:196](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:196) |
| Always-INCOMPLETE provenance could pass | **Resolved.** A complete record must be ATTESTED; individual omissions must produce exact missing-item lists. [test_browser_seal_step6.py:320](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:320) |
| Switch-off test never loads | **Resolved.** It now loads into a fresh page with the shipped switch setting and checks the restored result. [test_browser_seal_step6.py:348](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:348) |
| Field tests delete required siblings | **Partially resolved — MINOR remains.** The support test isolates `f`; the page-software and chosen-alternative cases still omit siblings. [test_browser_seal_step6.py:406](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:406) |

**2. Schema totality, completeness and honest records**

The schema wrapper contains the reported JSON-value exceptions, and the reported sealed-reader type gaps are closed. I found no additional confirmed escaping exception in a sealed reader.

It is not literally complete field typing: `R.context0.live` validates `ccShift` and anchors, while other control fields later undergo string conversion in `_sealCtxRead`. Exceptions during that later judgment are contained by `sealedState`. [index.html:7263](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7263), [index.html:9110](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9110), [index.html:9561](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9561)

I found **no concrete honest-producer rejection**. All five producer names remain accepted, global-method “not run” evidence remains accepted, and local records have their own form. New tests exercise global-method and Batch persistence. Universal compatibility remains unverified here: browser tests could not execute, and step 6 still lacks a dedicated “Use this solution” persistence round trip. [index.html:7258](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7258), [index.html:7285](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7285), [test_browser_seal_step6.py:528](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:528), [test_browser_seal_step6.py:548](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:548)

**3. Loaded values can still abort loading — MAJOR**

On an otherwise well-formed legacy provenance record, set:

```js
record.backgroundVerdict.effect = {
  method: "toString",
  window: [0, 1],
  k: 1
};
```

`_sealEffectExact` indexes an ordinary object with `e.method`. `"toString"` resolves to an inherited function, so `want.slice()` throws **`TypeError: want.slice is not a function`**. `"constructor"` and `"__proto__"` also reproduce it. This lookup differs from the Python dictionary lookup it claims to mirror. [index.html:7235](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7235), [fitting.py:3352](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/fitting.py:3352)

The sealed schema catches this, but `_fitRecordWellFormed` and `_loadedTabProvenance` do not. Both loaders read provenance before sealed dispatch, so even a valid seal accompanied by this provenance can fail loading. I reproduced the exception through the extracted production project loader. `_fitRecordRows`’s containment cannot help because execution has not reached it. [index.html:12054](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:12054), [index.html:13857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13857), [index.html:14064](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14064)

Use an own-property lookup or `Map`, and make legacy-record validation reject rather than throw.

I found no additional confirmed markup-insertion path. Present falsy seals still dispatch by property presence and avoid legacy reconstruction. [index.html:12051](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:12051), [index.html:14098](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14098)

**4. Test discrimination and switch-off behavior**

**MINOR — two field cases still pass for unrelated reasons.**

- The page-software test replaces the entire software record with `{role: 7}`, removing required fields.
- The chosen-alternative test supplies only `shiftName: '<b>'`, removing three required numeric fields. `'<b>'` is valid text; rejection does not test its type.

I confirmed both remain rejected when their named field’s type check is relaxed to `any`. Preserve valid siblings and change only the field under test. [test_browser_seal_step6.py:407](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:407)

The other named round-2 test weaknesses are addressed as listed above. No test covers the inherited-method loader failure.

With the switch off, I found no ordinary save/load regression. Literal identical behavior is broader than the implementation: renderer exception containment and the software-role guard apply unconditionally, improving malformed-record handling even with the switch off. [index.html:9906](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9906), [index.html:9933](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9933)

Validation: extracted production-function probes confirmed the fixes and remaining failure. Selected JavaScript suites: **182 passed, 3 failed** because temporary storage was unavailable. Browser assertions did not run: Chromium setup failed creating its artifacts directory under the read-only sandbox.

VERDICT: NO-GO
