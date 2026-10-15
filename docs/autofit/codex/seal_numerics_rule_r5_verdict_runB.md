**The three round-4 MAJOR defects are resolved. Three MINOR gaps remain, including the previously reported recovery-test gap. No BLOCKER or remaining MAJOR defect was reproduced.**

1. **Round-4 findings, combining both runs**

| Finding | Status |
|---|---|
| Overlapping checks permit unlimited automatic numerics changes | **Resolved.** A matching reply cannot replenish the allowance while another check remains in flight. [index.html:9121](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9121) |
| An earlier staged answer acquires the current epoch at commit | **Resolved.** Outcomes retain their sending epoch; commit checks every constituent before creating an entry. [index.html:9129](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9129), [index.html:9208](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9208) |
| A split shows cached confirmation or accepts a staged commit | **Resolved.** Split guards cover cache reads, entry creation, commit and displayed confirmation. [index.html:9136](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9136), [index.html:9292](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9292) |
| Background triggers continue checking during a split | **Resolved through `_ensureVerified`.** [index.html:9260](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9260) |
| Missing effect fields and incorrect window/coordinate dimensions | **Reported examples resolved; completeness gap remains below.** [fitting.py:3345](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3345) |
| A → B → A test misses the vulnerable recovery interval | **Unresolved.** The added assertion observes the wrong interval. |
| Missing concurrent-worker coverage | **Partially resolved.** Two owners are exercised, but the adverse completion order is uncontrolled. |

The inherited digest limitations remain stated limitations: excluded verifier arithmetic, function-only app closure, reviewed equivalence assertions and history protection conditional on `main` having a manifest. [numerics_digest.py:40](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:40), [test_numerics_version.py:46](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:46)

2. **Page invariants and adversarial sequences**

I found no remaining path that caches or commits a confirmation without current-epoch, current-numerics answers. Both cache writers use `_verdictEntry`; staged commits additionally require every answer. Unreachable outcomes retain their sending epoch. Producer attachment retains its ownership checks. Detached answers carry provenance but must be judged with `_outcomeCounts` when consumed. Fit replies retain the fit’s starting epoch, preventing a late old fit from moving numerics backwards. [index.html:9153](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9153), [index.html:9237](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9237), [index.html:8374](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:8374), [index.html:8443](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:8443)

My controlled sequence combined two installed seals, a staged Auto-Fit anchor answered under A, discovery of B, an old unreachable check, current B replies and an opposing worker during replacement checks. Results:

- The old anchor plus current final answer could not commit.
- The opposing replacement reply produced a split after bounded requests.
- Both seals read unconfirmed; cache reads and staged commit refused.
- Ordinary background triggers issued zero requests.
- “Check again” recovered confirmation once replies stabilized.

The literal header statement that nothing is checked under a split is broader than implementation: direct `_verifySeal` and `_verifyStagedCheck` calls can still send requests. Their results cannot create confirmation or commit during the split; the supported background trigger is guarded. [index.html:9196](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9196), [index.html:9223](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9223)

3. **A single ordinary deployment works**

I exercised three distinct seals with B discovered first, two late A replies and three replacement B replies, across **all 120 completion orders**. Every sequence finished with all seals current and no split. Late replies cannot move the epoch back. [index.html:9091](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9091)

4. **Remaining findings and test sensitivity**

- **MINOR — recovery assertion still misses epoch revival.** At the new assertion, the page still knows B, so A’s cache is rejected by its numerics key even with the epoch guard removed. The vulnerable interval begins **after** the held A reply changes the page back to A and starts another check. My mutation probe returned `pending` at the test’s assertion, then incorrectly `current` during that unobserved interval, and `current` finally. Hold the replacement request and assert there. [test_browser_seal_step4.py:743](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:743)

- **MINOR — concurrent-worker test does not force the defect’s completion order.** After B discovery, its handler assigns A to the next request and B to the following request. If A completes first, even an implementation missing the in-flight guard splits immediately and satisfies the assertions. My mutation probe demonstrated this; B-before-A exposed the defect. Explicitly release B before A. [test_browser_seal_step4.py:790](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:790)

- **MINOR — manual-effect anchor count remains unchecked.** `{"method":"manual","anchors":[]}` and a single two-number anchor pass form validation. The producer emits `manual` only with at least two anchors; otherwise it emits `manual-line`. Both malformed records returned `unconfirmed/numerics` with an unreadable request instead of `mismatch/schema`. Require at least two anchors. [fitting.py:2190](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:2190), [fitting.py:3353](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3353)

Validation: **113 targeted JavaScript tests passed; 14 digest tests passed, one skipped; 95 verifier cases and 16 honest-record cases passed using in-memory fits and the real endpoint.** All five new effect-form tests failed when their checker was disabled in memory. No arithmetic regression or honest-record rejection surfaced. Full Playwright integration was not run; the broader JavaScript run encountered Python-helper failures under the read-only temporary-directory restriction. Checkout unchanged.

**VERDICT: NO-GO**
