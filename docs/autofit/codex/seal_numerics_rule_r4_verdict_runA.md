**NO-GO: three MAJOR page issues remain. No BLOCKER found.** The reported server fixes work, but form validation still has a MINOR structural gap.

The round-3 findings from both runs resolve as follows:

| Finding | Round-4 status |
|---|---|
| Mixed-numerics staged pair commits | **Resolved for A/B answers**, including outdated-plus-unreachable. The guard now checks constituents before aggregation. [index.html:9207](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9207) |
| Earlier epoch’s confirmation revives | **Partially resolved.** Existing cache entries have epochs, but staged answers can acquire a later epoch at commit; see below. [index.html:9135](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9135) |
| Mixed workers recheck indefinitely | **Partially resolved.** Strict single-request alternation stops; overlapping checks can continue indefinitely. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102) |
| Missing component id/shape types and area | **Resolved.** [fitting.py:185](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:185) |
| Missing background-verdict types | **Resolved for the reported types.** Structural completeness remains incomplete below. [fitting.py:3339](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3339) |
| Saved-data finiteness precedes form | **Resolved.** [app.py:1407](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1407) |
| Missing real staged-pair / A → B → A / alternating-worker tests | **Partially resolved.** Real-pair coverage added; epoch and concurrent-worker gaps remain. [test_browser_seal_step4.py:696](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:696) |
| asteval/BLAS checked against themselves | **Resolved.** Expected values now come independently from metadata/configuration. [test_fit_recording.py:66](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_fit_recording.py:66) |
| `_precision_words` wording counted | **Stated limit**, with equivalence re-baselining available. [numerics_digest.py:12](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:12) |

The inherited digest limits also remain: verifier arithmetic is excluded, the app closure follows functions rather than module data, equivalence requires a reviewed assertion, and history protection depends on `main` having a manifest. [numerics_digest.py:43](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:43), [numerics_digest.py:109](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:109), [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

Across deployments and mixed workers, these issues remain:

- **MAJOR — overlapping checks defeat the retry bound.** With two installed seals, discover B; let one replacement answer B, settling the epoch; then let the other answer A, starting another deployment. Repeat with identities reversed. I reproduced **23 requests, 11 epoch changes, two further requests pending, and `_numericsSplit === false`**. One matching reply resets the allowance before another outstanding reply changes identity. This sequence can continue indefinitely without user action. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102), [index.html:9118](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9118)

- **MAJOR — staged answers can revive an earlier epoch’s confirmation.** Check a staged record under A in epoch 0; other requests discover B, settle B, then discover A in epoch 2. The original staged answer still has `outdated: false` and key A. `_commitStaged` accepts it, and `_verdictEntry` stamps it with **epoch 2**, although that record received no epoch-2 recomputation. My probe committed and returned `current`. Individual outcomes need epoch provenance checked at commit; assigning the epoch only when constructing the cache entry is insufficient. [index.html:9073](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9073), [index.html:9135](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9135), [index.html:9209](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9209)

- **MAJOR — split state does not reliably suppress confirmation.** A staged check can discover B and commit its consistent answer while B is unsettled. A subsequent A reply sets `_numericsSplit`, but `sealedState` reads the cached confirmation **before** checking split. I reproduced `split: true` alongside `state: current`. Split also lacks a guard in `_ensureVerified`: five ordinary background triggers issued five additional checks while split remained true. [index.html:9284](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9284), [index.html:9252](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9252)

I found no permanently unrecoverable seal once workers become stable and reachable: “check again” clears split and starts a replacement attempt. The supplied single-tab recovery sequence works. That does not resolve the concurrent retry cycle or stale staged provenance. [index.html:9249](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9249)

**The server’s form check is not yet complete. MINOR — background tuple dimensions are unchecked.** `_BG_EFFECT_T` accepts `window: []` and `anchors: [[1]]`; the producer emits two-element windows and two-coordinate anchors. These dimensions require no recomputation to judge. Both malformed examples passed `response_form_failure` and returned `unconfirmed/numerics` under another identity, rather than `mismatch/schema`. The reported scalar-type omissions and finiteness ordering are fixed. [fitting.py:3339](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3339), [fitting.py:2187](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:2187)

**The tests detect their narrow cases, but not every named guarantee.**

- The real staged A/B pair exercises the repaired constituent guard; outdated-plus-unreachable also rejected in my page-function probe.
- All **nine form/precedence cases failed** when early form validation was disabled in memory. Both recording assertions failed with deliberately incorrect asteval/BLAS values.
- **MINOR — the A → B → A test does not protect epoch invalidation.** Removing `v.epoch === _numericsEpoch` still satisfies its observed split and final-confirmation states. The incorrect confirmation appears during recovery, before the replacement finishes; the test waits past that interval. I reproduced this distinction. [test_browser_seal_step4.py:731](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:731)
- The alternating-worker test uses one seal and misses the overlapping-check sequence above. [test_browser_seal_step4.py:744](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:744)

Read-only validation: **100 JavaScript tests passed; 14 digest tests passed, one skipped; 90 server cases passed through the real endpoint using an in-memory fit; five recording cases and 22 honest-record cases passed.** No fitted-arithmetic regression or honest-record rejection surfaced. Full browser integration and the historical 1b corpus were not run. Checkout unchanged.

VERDICT: NO-GO
