**NO-GO for steps 3–4 as complete.** I found three MAJOR issues/gaps and one MINOR false-stale case. I found no new numerical regression in the ordinary fit-producing paths.

1. **User-visible behaviour**

   The existing result application and consumers remain authoritative. Run Fit still applies the backend reply through `applyBackendResult`; the seal is added alongside the existing fields. Auto-Fit similarly publishes its existing result with an additional seal. Local/Batch retain the previous optimizer and commit arithmetic. See [index.html:9666](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9666), [index.html:8685](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8685), and [index.html:10243](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10243).

   The deliberate per-tab method change is present. I found no ordinary-input producer path newly throwing or changing fitted numbers. However, `_SEAL_AUTHORITATIVE` is currently an unused declaration, rather than a switch enabling the planned verification flow.

2. **Seal contents and isolation**

   Run Fit correctly snapshots `opts.startPeaks || state.peaks`, context, request and selected samples before upload. Auto-Fit captures each request’s inputs before its corresponding upload. Final seals use `structuredClone` followed by recursive freezing, so ordinary record objects share no mutable state with the producer. See [index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9572), [index.html:8458](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8458), and [index.html:7121](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7121).

   Server O is copied from the reply without rewriting it. Local O contains the inputs, inventory, final working model, curves, statistics and support needed by its check, using the existing committed solution. See [index.html:10294](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10294).

   **MINOR — R does not always equal the uploaded samples, causing false STALE.** `_roiSelect` preserves an input `-0`, but upload’s `String(v)` sends `0.0`. R retains `-0`; `_jsonEqual` uses `Object.is`, so the honest server reply’s `+0` fails the samples check. I reproduced `_bindOne` returning `samples` for this case. The same issue applies to signed-zero counts. Normalize this transport equivalence consistently in recording and binding, without a tolerance. See [index.html:6987](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:6987), [index.html:8850](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8850), and [index.html:8969](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8969).

3. **Bindings and states**

   The principal checks are present: recorded finite shift, link graph, spectrum selection, rebuilt request, background values/effect, local input reconstruction, structure-preserving local projection, bounds, determinacy, and exact numerical reconstruction. Auto-Fit checks both recorded acceptances, anchor gates and final-model/context derivation. See [index.html:8925](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8925), [index.html:8948](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8948), and [index.html:8998](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8998).

   **MAJOR — an Auto-Fit numerical mismatch can become UNCONFIRMED instead of STALE.** `_verifyStaged` uses `Promise.all`. If either request rejects, the other request’s `mismatch` is lost, and `_verifySeal` records only “unreachable.” I reproduced `{verdict: undefined, unreachable: true}` with one statistics mismatch and one transport failure. If the other check is still outstanding, this also reports UNCONFIRMED prematurely. Retain each check’s outcome and apply §6.3’s precedence: mismatch, outstanding, unconfirmed, consistent. See [index.html:9045](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9045) and [index.html:9063](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9063).

4. **Verification ownership**

   Installed-seal verification correctly checks the latest attempt, live owner object, currently installed seal, and—producer-bound—the current operation and active tab. Background verification does not claim a fit operation. Discard clears its attempt; a subsequent `_ensureVerified` can recover. Explicit retry after an uncached unreachable result works. See [index.html:9054](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9054) and [index.html:9078](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9078).

   **MAJOR — the planned STAGED transaction ownership is unimplemented.** `_verifyStaged(checks)` accepts no owner, operation, transaction identity or staged-object identity; it simply posts and aggregates. Auto-Fit never invokes staged verification before publishing. Thus step 4 has no guarded transaction path to test for supersession during either verification, rollback on unconfirmed, or commit with both verified answers. Keeping today’s behaviour while disabled is correct, but the implementation behind the switch is missing. See [index.html:9044](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9044), [index.html:8686](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8686), and [plan:268](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:268).

5. **Local extractions**

   **Yes:** inventory, link ordering, propagation assignments and clamp preserve the old code’s semantics. Mechanical comparisons against `70e1097` confirmed identical inventory text, link-order statements and clamp statements after ignoring indentation. Propagation retains the same fields, lookup and arithmetic. See [index.html:9889](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9889), [index.html:9932](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9932), and [index.html:9953](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9953).

6. **Tests**

   **MAJOR — the ownership test does not create its named scenario, and required negatives are missing.** It calls `_installFitOp(owner, _newFitOp(owner))`, but the function accepts one **operation** argument. Passing the tab returns without installing anything; the tested operation was never current. I confirmed that the previous operation remains installed. The test also never switches tabs despite its name. See [test_browser_seal_step4.py:164](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_step4.py:164) and [index.html:8322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8322).

   Missing step 3–4 coverage includes actual Use-solution and Batch seals; local energies/net/held-value and consistent lock/link substitutions; wrong-spectrum E; staged supersession at both checks; mixed Auto-Fit verdicts; producer tab-switch recovery; replaced-seal/reused-tab-id replies; and background verification preserving an existing fit operation. These are explicitly relevant to [plan:320](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:320). Persistence and consumer-presentation tests can remain with their later steps.

7. **Design rules**

   The shared context reader and extracted local routines generally respect “Two readings of one field.” The signed-zero transport/binding mismatch is an exception. The new numerical checks introduce no data-scaled acceptance tolerance; fixes should preserve that property.

Validation: **124 focused JS tests passed**, plus the in-memory reproductions above. The full suite could not be validated successfully in this read-only sandbox: Python-backed tests failed on denied temporary-file access. Browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
