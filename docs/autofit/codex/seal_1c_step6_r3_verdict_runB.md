Reviewed `seal-1c-s5..6ab526e`, read-only. **One MAJOR and two MINOR findings remain.**

**1. Round-2 findings, covering both runs**

| Finding | Status |
|---|---|
| Hostile engine/ID objects throw during schema checking | **Resolved.** Types are checked before coercion, and schema exceptions are contained. [index.html:7163](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7163), [index.html:7252](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7252) |
| Model parameter types unchecked | **Resolved for the reported cases.** Centre, width and amplitude require numbers; remaining fit fields require scalars. [index.html:7245](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7245) |
| Component `params: {}` accepted | **Resolved.** `area` is required and typed. [index.html:7278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7278) |
| Background-effect contents unchecked | **Original payloads resolved; validation still has an exception path**, described below. [index.html:7232](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7232) |
| Local background contents insufficiently typed | **Resolved for the reported gap.** Certificate fields and effect form are checked. [index.html:7300](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7300) |
| Legacy certificate/effect crashes Results | **Original renderer failures resolved.** Both payloads are rejected, and `_fitRecordRows` contains formatting exceptions. A new legacy-validation crash remains below. [index.html:12058](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:12058), [index.html:9906](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9906) |
| `SETTLE` masks missing loader verification | **Resolved in the ZIP regression test.** It now uses `WAIT`, which starts no checks. [test_browser_seal_step6.py:115](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:115) |
| Auto-Fit test does not establish both checks | **Resolved.** Interception precedes loading, two requests are required, and failing E must produce STALE. [test:178](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:178) |
| Always-INCOMPLETE provenance passes | **Resolved.** A complete record must be ATTESTED, and each missing-item list is checked exactly. [test:320](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:320) |
| Switch-off test never loads | **Resolved.** It now loads into a fresh page with the shipped switch setting. [test:348](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:348) |
| Field tests delete siblings | **Partially resolved — MINOR remains.** The support case is isolated; the page-software and chosen-alternative cases still delete required siblings. [test:406](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:406) |

**2. Schema totality, completeness and honest seals**

The `_sealSchemaFailure` boundary now contains the reported exceptions. **Completeness remains imperfect — MINOR:** `R.context0.live` checks only `ccShift` and `anchors`, leaving fields subsequently coerced by the context-key reader unchecked. For example, `live.fitMethod = {toString: 0}` passes the schema but throws when `_sealCtxRead` reads it. `sealedState` contains that exception, so this is a validation gap rather than another demonstrated loading crash. [validation:7263](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7263), [reader:9109](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9109), [containment:9561](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9561).

I found **no concrete rejection of an honest producer’s seal**. The producer enumeration, not-run variants, local form and Auto-Fit E checks accommodate their intended outputs. Global-method and Batch round-trip tests have been added. However, browser execution was blocked, and “Use this solution” still lacks a persistence round-trip test, so universal compatibility is not established by this run. [schema:7258](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7258), [not-run:7285](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7285), [new tests:528](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:528).

**3. A loaded legacy value can still abort loading — MAJOR**

On an otherwise well-formed legacy record, use:

```js
record.backgroundVerdict.effect = {
  method: "toString",
  window: [0, 1],
  k: 1
};
```

I reproduced `_loadedTabProvenance({record})` throwing:

```text
TypeError: want.slice is not a function
```

`_sealEffectExact` indexes an ordinary object without checking ownership. `"toString"`, `"constructor"` and `"__proto__"` select inherited values instead of the default field list. `_fitRecordWellFormed` calls this helper without containment. Consequently, loading saved provenance—or dropping a legacy fit carrying this record—throws before completing. The renderer’s new catch cannot help. [lookup:7235](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7235), [validator/drop:12054](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:12054), [project loader:14064](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14064), [spectrum loader:13857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13857).

Use an own-property lookup or `Map`, and make legacy validation return rejection on exceptions.

I found no additional confirmed markup-insertion path through the reviewed sealed readers, nor a sealed project/spectrum record reaching legacy restoration. Both loaders dispatch on seal presence. [spectrum:13861](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13861), [project:14096](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14096).

**4. Tests and switch-off behavior**

**MINOR — not every field test discriminates its named check.** I removed the `role` and `shiftName` type checks independently in memory; their existing cases still produced the expected rejection because required siblings were absent. Moreover, `shiftName: "<b>"` is valid text; the renderer escapes it. Preserve complete sibling fields and mutate only the target field to an invalid type. [tests:407](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:407), [renderer:10015](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:10015).

I found no ordinary switch-off save/load regression. Literal “everything unchanged” is broader: `_fitRecordRows` containment is unconditional, so malformed legacy records now behave differently even with the switch off. [index.html:9906](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9906).

Validation: extracted production-function probes confirmed the findings and original-payload fixes. Selected JavaScript suites reported **182 passed, 3 failures involving unavailable temporary storage**. Browser tests stopped at fixture setup because Playwright could not create its artifacts directory; application assertions did not run. No files were changed.

**VERDICT: NO-GO.**
