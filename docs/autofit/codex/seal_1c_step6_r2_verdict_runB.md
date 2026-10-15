(Note: edits for round 3 began in this checkout while run B was finishing; run B states it reviewed the committed fbe389b.)

**NO-GO for `seal-1c-s5..fbe389b`.** Three MAJOR defects and the MINOR test finding remain. Uncommitted edits appeared during this review; the findings below were reproduced against committed `fbe389b`, and line numbers refer to that snapshot. I changed no files.

1. **Round-1 findings: partially resolved.**

| Finding from either run | Status |
|---|---|
| Honest `{ran:false, reason}` starts/required rejected | **Resolved.** Both variants are accepted. [index.html:7264](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7264) |
| Unchecked starts counts, alternative counts and numeric lists | **Resolved.** The complete starts spec types these fields. [index.html:7206](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7206) |
| Unchecked software `role` | **Resolved.** O rejects `role`; permitted page/legacy roles must be strings; the renderer also guards `.replace`. [index.html:7269](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7269), [index.html:9830](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9830) |
| Unchecked background verdict | **Partially resolved.** Direct fields are typed; `effect` remains unchecked internally. See MAJOR below. |
| Primitive seal crashing WeakMap readers | **Resolved for the reported cases.** Primitive/list values receive an object wrapper. [index.html:11939](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11939) |
| Present falsy seal entering legacy restoration | **Resolved.** Both loaders dispatch by presence. [index.html:13757](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13757), [index.html:13994](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13994) |
| Loaded legacy provenance crashing Results | **Partially resolved.** The `role:7` case is fixed; malformed certificates still pass and crash. See below. |
| Local O’s missing designation/statistics/certificate checks | **Substantially resolved.** Those checks are present; nested background data still use `any`. [index.html:7275](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7275) |
| STALE/export/PNG provenance omissions | **Resolved for readable records.** See answer 4. |
| Tests that do not discriminate | **Unresolved — MINOR.** See answer 5. |

2. **The schema is not yet complete or safe.** The remaining findings are:

- **MAJOR — Malformed objects can throw during installation instead of becoming PEAKS-ONLY.** A seal containing `engine:{"toString":0}` throws at `Object.hasOwn(PRODUCERS, seal.engine)`. An otherwise valid seal with `R.pageModel[0].id={"toString":0}` similarly throws in the ID validator. `_installSavedSeal` invokes the schema without containment, so both loaders can abort. These are ordinary JSON values; no executable payload is needed. Type engine/producer and model ID/link values before coercing them. [index.html:7237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7237), [index.html:17419](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:17419), [index.html:11944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11944).

- **MAJOR — Background-effect contents still reach an unsafe reader.** `background_verdict.effect.window=[{"toString":0},1]` passes the schema because effect values are `any`, then `_fitRecordRows` throws at `window.join('-')`. A binding failure does not contain this: STALE records retain their view and `_exportRecordOf` returns that record to export readers. Type the effect’s consumed fields. [index.html:7225](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7225), [index.html:9818](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9818), [index.html:9569](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9569).

- **MAJOR — Legacy provenance still admits certificates that crash Results.** An otherwise well-formed record with `certificate:{"check":{"toString":0}}` passes `_fitRecordWellFormed` and `_loadedTabProvenance`. `_fitRecordRows` then throws when concatenating `c.check`, aborting the new no-fit Results branch. Validate the certificate’s consumed fields or make the reader total. [index.html:11955](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11955), [index.html:9826](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9826), [index.html:10968](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:10968).

**The seven claimed shared specs are identical:** I mechanically compared MOVE, NOT_RUN, STARTS, REQUIRED, CERTIFICATE, SUPPORT and STATISTICS after normalizing Python tuples to JavaScript arrays. [index.html:7204](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7204), [fitting.py:3269](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/fitting.py:3269).

I found no remaining concrete honest-producer rejection. Auto-Fit’s E receives the same R/O checks. However, the tests do not establish every producer’s persistence round trip, so universal compatibility remains unproven. [index.html:7296](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7296).

3. **Loaded values can still crash readers**, as reproduced above. The original starts-count markup insertion is closed, and I found no additional concrete markup-injection path in the inspected sealed readers. Present falsy seals now avoid legacy restoration in both formats. History reinstall remains the explicitly deferred step-7 scope.

4. **Provenance presentation now satisfies the reported §8.3 gaps for readable records, including STALE.** `_sealProvenanceOf` uses any available view, and Results, CSV/XLSX, both TSV branches and PNG metadata consume it. The classification uses the intended commit, cleanliness and digest fields. Malformed records remain subject to the crashes above. [classification/accessor:7308](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7308), [Results:11032](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11032), [TSV:14204](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14204), [PNG:14623](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14623), [XLSX/CSV:14745](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14745).

5. **No, the tests do not each discriminate their named defect — MINOR.**

- `SETTLE` still calls `_ensureVerified` itself, masking omission of loader-triggered inactive-tab verification. [test_browser_seal_step6.py:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:27).
- Auto-Fit still collects requests after loading and never asserts them or independently tests rejection of E. [test:178](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:178).
- Provenance tests still permit an always-INCOMPLETE implementation with a nonempty missing list. [test:297](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:297).
- “Switch off saves and loads” still never loads. [test:306](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:306).
- Several new field tests also delete required sibling fields, so they do not isolate the named type check—for example, replacing support with only `{f:'x'}`. [test:362](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:362).

With the switch off, I found **no ordinary-workflow regression by inspection**. Literal unchanged behavior is broader than the evidence: the role-rendering guard and frozen-result mutation guards are unconditional.

Validation: extracted production-function probes reproduced all three MAJOR findings against `fbe389b`. Selected JavaScript suites reported **108 passed, 3 environment-related failures** involving unavailable temporary storage. Browser pytest could not start under the read-only sandbox.

**VERDICT: NO-GO.**
