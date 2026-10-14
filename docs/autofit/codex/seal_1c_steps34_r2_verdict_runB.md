Steps 3–4 remain **NO-GO**. The principal round-1 binding and aggregation defects are fixed, but the staged transaction still cannot reliably transfer its verified answers into a newly created seal.

**1. Round-1 findings, both runs**

| Finding | Status |
|---|---|
| Signed-zero / wire-identity false STALE (A, B) | **Resolved for ordinary records.** Record comparisons equate signed zeros and omit undefined object fields. [index.html:8858](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8858) |
| Auto-Fit producer-setting continuity and anchor identity (A) | **Resolved.** Both producer contexts must match, and `require_component` must identify the anchor. [index.html:8952](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8952) |
| Sample memo ignores edits in place (A) | **Resolved for ordinary dense arrays.** Identity and copied values are checked. [index.html:8931](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8931) |
| Mismatch lost on rejection; premature UNCONFIRMED (A, B) | **Resolved.** Individual outcomes survive rejection; mismatch wins immediately, otherwise outstanding checks delay settlement. [index.html:9062](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9062) |
| Missing staged ownership mechanism (A, B) | **Partially resolved — MAJOR remains.** Owner/operation/transaction guards exist; staged-data integrity and commit transfer remain incomplete. See answer 4. |
| Explicit retry blocked by cached verdict (A) | **Original case resolved; “always” remains incomplete — MINOR.** An outstanding attempt still blocks explicit retry. [index.html:9155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9155) |
| Supersession test never installs the operation; no tab switch (A, B) | **Resolved.** It now claims successive operations and separately switches tabs. [test_browser_seal_step4.py:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:158) |
| Missing negative cases / producer coverage (A, B) | **Substantially improved, partially resolved.** Remaining weaknesses are detailed in answer 6. |
| JSON-stringified identity assertions conceal differences (A) | **Partially resolved.** The shared assertions became strict, but Auto-Fit request/context/O assertions still stringify. [test_browser_seal_step3.py:105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step3.py:105) |

The unused switch and absent Auto-Fit integration are appropriately deferred to step 7; they are not independently grounds for rejecting this round. [plan:358](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/docs/superpowers/plans/2026-10-14-seal-1c-page.md:358)

**2. Record equality**

The intended rule is sound for finite JSON-shaped records: `-0` and `0` have the same transported value; undefined object properties disappear; explicit null remains distinct from absence; NaN remains distinct from null. This agrees with the verifier’s typed numerical equality. Keeping `_sameModel` strict is correct for proving implementation identity, while bindings use `_sameRecordModel`. [fitting.py:3171](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/fitting.py:3171), [index.html:7093](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:7093), [index.html:7108](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:7108)

**MINOR — sparse arrays break the stated rule.** `_jsonEqual` uses `x.every`, which skips holes. I reproduced:

```js
_jsonEqual(Array(1), [123]) // true
_jsonEqual([123], Array(1)) // false
```

Their JSON representations are `[null]` and `[123]`. Thus genuinely different serialized records can compare equal, and equality is asymmetric. Iterate every index, including holes. I found no ordinary producer creating sparse arrays. [index.html:8863](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8863)

**3. Auto-Fit evidence**

The reported bypasses are closed. Different producer settings fail continuity; matching settings that omit or name another anchor fail identity; rebuilt requests bind those settings to each request. Honest production chooses the same stringified Graphite-or-first ID and passes it to both fits, matching the new predicate. I found no new honest-Auto-Fit binding failure. [index.html:8952](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8952), [index.html:8986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8986), [index.html:8585](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8585), [index.html:8653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8653)

This proves the request asked about the anchor; `required` remains acceptance **as recorded**, as designed. [fitting.py:3296](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/fitting.py:3296)

**4. Precedence and staged transactions**

Installed-seal aggregation now implements the requested precedence. Superseded installed attempts cannot attach through the latest-attempt, owner, seal, operation and active-tab guards. [index.html:9068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9068), [index.html:9129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9129)

**MAJOR — staged verification does not complete the planned lifecycle.**

- **Answers disappear across seal creation.** `_makeSeal` deep-clones R/O, whereas `_commitStaged` finds answers using reference identity. I reproduced two consistent staged checks → `_makeSeal(...)` → commit returning `true`, with **no cached verdict**. It also deletes the transaction before returning this apparent success. This conflicts with §9’s requirement to enter both answers at commit. [index.html:7127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:7127), [index.html:9112](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9112), [plan:268](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/docs/superpowers/plans/2026-10-14-seal-1c-page.md:268)
- **Staged contents are not protected.** `_verifyStagedCheck` checks transaction ownership after awaiting, but neither snapshots/freezes R/O nor checks whether their contents changed. I sent count `2`, changed the supplied R to count `999` while pending, and received `consistent` stored against the changed R. Operation/transaction supersession is guarded; supersession of the checked contents is not. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9102)

The manager needs immutable staged records and an explicit transfer of their answers into the final seal.

**MINOR — explicit retry is not unconditional.** `_ensureVerified(owner, true)` returns null when the same seal has an outstanding attempt. I reproduced zero additional requests. A hanging attempt therefore defeats “check again.” Apply the in-flight deduplication only to ordinary background triggers, allowing explicit retry to supersede it. [index.html:9151](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9151)

**5. Switch-off behavior**

I found no shipped numerical regression. Existing application paths remain authoritative, with seals added alongside results. The per-tab method behavior is the planned change. [index.html:9739](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9739), [index.html:9754](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9754), [index.html:3924](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:3924)

The local-engine replay against `70e1097` produced **121 bit-identical results, zero differences, zero skips**.

**6. Test strength**

The new ownership, cached-retry, signed-zero, raw-edit, producer-continuity and mixed-outcome cases materially improve coverage. Use-solution and Batch now exercise actual producer paths. However, **not every test isolates its named defect**:

- The staged success test installs a completed seal **before** verification and checks its frozen objects. It misses both staged defects above. [test_browser_seal_step4.py:444](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:444)
- Retry tests cover completed attempts only. [test_browser_seal_step4.py:228](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:228)
- The held-value test also changes the parameter inventory, so it fails at `inventory` even if held-value projection checking is removed. [test_browser_seal_step4.py:289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:289)
- Wrong-spectrum E changes only R.counts; disagreement with E.O still catches it if raw-spectrum binding is removed. Use a coherent R/O pair from another spectrum. [test_browser_seal_step4.py:348](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:348)
- Outstanding coverage lacks **unreachable + outstanding**, the original premature-UNCONFIRMED case. [test_browser_seal_step4.py:403](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:403)

Validation: **56 focused JS tests passed**, plus the 121-tab replay and extracted-function reproductions. Browser suites were inspected, not rerun in this read-only environment. No files changed.

VERDICT: NO-GO
