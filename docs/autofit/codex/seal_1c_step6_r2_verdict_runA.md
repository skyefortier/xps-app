Two **MAJOR** correctness defects remain, plus the unresolved **MINOR** test-discrimination finding. No files were changed.

**1. Round-1 findings, covering both runs**

| Finding | Status |
|---|---|
| Honest `{ran:false, reason}` starts/required rejected | **Resolved.** Both variants are accepted. [index.html:7264](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7264) |
| Untyped starts counts, numeric lists and alternative counts | **Resolved.** The copied starts spec covers them. [index.html:7204](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7204) |
| Software `role` reaching readers unchecked | **Resolved.** Server O rejects `role`; page software types it; the renderer checks for text. [index.html:7269](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7269), [index.html:9830](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9830) |
| Incomplete nested-field validation, including background verdict | **Partially resolved.** Top-level verdict fields are typed; its `effect` remains arbitrary. Other schema gaps remain below. [index.html:7225](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7225) |
| Primitive seals crashing WeakMap readers; falsy seals entering legacy restoration | **Resolved for the reported values.** Presence dispatch and object containment handle strings, booleans, numbers, arrays and null. [index.html:11939](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11939) |
| Loaded legacy provenance crashing Results | **Partially resolved.** The `role` reproduction is fixed, but other accepted record fields still crash the same renderer; see answer 3. [index.html:11955](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11955) |
| Missing STALE/PNG provenance | **Resolved for the classification required by §8.3.** See answer 4. |
| Tests not discriminating their named behavior | **Unresolved.** See answer 5. |

**2. The schema is not yet complete or safe.**

**MAJOR — schema rejection itself can abort loading.** On an otherwise valid seal, either mutation below makes `_installSavedSeal` throw `Cannot convert object to primitive value`:

```js
seal.engine = {toString: 0};
seal.R.pageModel[0].id = {toString: 0};
```

The first reaches `Object.hasOwn(PRODUCERS, seal.engine)` without a string check; the second reaches `String(p.id)` without a scalar check. The installer calls the schema outside a catch, so these exceptions escape both loaders instead of producing PEAKS-ONLY. I reproduced both with extracted production functions. [engine check:7237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7237), [ID check:17419](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:17419), [installer:11944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11944).

The completeness claim also exceeds what is checked: model validation covers IDs/links/colours, not model parameter types; component parameters are checked only when present. A string model centre and `params:{}` both pass `_sealSchemaFailureUncached`. Missing `area` subsequently throws in view construction, although `sealedState` catches that case. [model check:7233](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7233), [parameter check:7258](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7258), [area reader:7346](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7346).

**The seven claimed server specs are identical.** I mechanically compared their evaluated structures against Python’s definitions; all seven matched. The starts/required union also matches the server. [page specs:7202](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7202), [server specs:3269](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/fitting.py:3269), [server union:3400](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/fitting.py:3400).

I found no further honest-producer rejection by inspection. That is not a verified universal round-trip result: actual global-method, Use-this-solution and Batch persistence remain untested here.

**3. Loaded values can still crash readers.**

**MAJOR — legacy provenance validation still admits values that crash Results.** Starting with an otherwise well-formed legacy record, either of these is accepted:

```js
record.certificate = {check: {toString: 0}};
record.backgroundVerdict.effect = {window: [{toString: 0}]};
```

`_loadedTabProvenance` accepts both; `_fitRecordRows` then throws `Cannot convert object to primitive value`, respectively during concatenation and `window.join('-')`. These are representable JSON values. I reproduced acceptance followed by the exception.

The cause is `certificate: ['null', ['map', 'any']]` and the equally unrestricted background `effect`. Results invokes this renderer without containment. Type the fields actually consumed, or make their formatting total. [validator:11955](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11955), [effect reader:9818](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9818), [certificate reader:9826](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9826), [Results:10968](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:10968).

The same unchecked background effect passes the sealed schema, so the “every reader field typed” claim also fails there.

I found no additional confirmed markup-insertion path through the newly typed text fields. Explicitly present falsy seals now avoid legacy restoration in both loaders. [spectrum dispatch:13757](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13757), [project dispatch:13994](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13994).

**4. Provenance classification now reaches the required presentations, including STALE.**

`_sealProvenanceOf` reads a readable record’s view independently of display eligibility. Results, CSV/XLSX, both TSV paths and PNG metadata now include the classification. Saves retain the seal’s provenance inputs; spectrum convenience statistics also include the classification. [helper:7321](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7321), [Results:11032](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11032), [CSV/XLSX:14745](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14745), [TSV:14202](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14202), [PNG:14622](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14622), [spectrum save:13428](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13428).

**5. No, the tests do not each discriminate the behavior they name. MINOR.**

The round-1 weaknesses remain:

- `SETTLE` starts verification itself, masking removal of loader-triggered inactive-tab verification. [test helper:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:27)
- Auto-Fit registers its request listener after loading and never asserts the collected requests or independently challenges the anchor check. [test:176](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:176)
- Provenance tests still permit an implementation that always returns INCOMPLETE with a nonempty missing list. [test:295](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:295)
- “Switch off saves and loads” still never loads. [test:306](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:306)

The added malformed-field and primitive-seal tests provide useful regression checks, but omit the failures above. No ordinary switch-off regression was found by inspection; comprehensive switch-off equivalence is not established.

Validation: extracted-function probes confirmed both MAJOR findings and the primitive/not-run fixes. The selected JS suites reported **137 passed, 3 failed**, with failures involving unavailable writable temporary directories. All **34 browser cases failed during fixture setup** because Playwright could not create its artifacts directory; their application assertions did not run.

**VERDICT: NO-GO.**
