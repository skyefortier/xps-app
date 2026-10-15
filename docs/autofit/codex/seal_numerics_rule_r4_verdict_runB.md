**NO-GO. Three MAJOR page defects remain, plus MINOR form-validation and test gaps. No BLOCKER found.**

**1. Status of the round-3 findings, combining both runs**

| Finding | Round-4 status |
|---|---|
| Staged A/B answers could commit | **Resolved for that case**, including an outdated answer paired with an unreachable outcome: constituent answers are checked before aggregation. Epoch reuse remains defective below. [index.html:9209](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9209) |
| Earlier epoch’s confirmation could revive | **Partially resolved.** Installed cache entries have epoch guards, but staged answers can acquire a later epoch at commit. [index.html:9144](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9144) |
| Mixed workers could recheck indefinitely | **Partially resolved.** The single-check alternating case stops; multiple concurrent checks can sustain the cycle. |
| Missing component id/shape/area and background-verdict types | **Reported cases resolved.** Background-effect structure still has a separate gap below. [fitting.py:165](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:165), [fitting.py:186](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:186) |
| Finiteness judged before form | **Resolved.** [app.py:1407](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1407) |
| Missing real staged-pair, A → B → A, and alternating-worker tests | **Partially resolved.** Scenarios were added, but epoch invalidation and concurrent-worker boundedness remain insufficiently tested. [test_browser_seal_step4.py:696](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:696) |
| Recording test compared asteval/BLAS against themselves | **Resolved.** Expectations now come from package metadata and NumPy configuration. [test_fit_recording.py:65](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_fit_recording.py:65) |
| `_precision_words` wording counts | **Stated limit**, with equivalence re-baselining available. [fitting.py:753](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:753), [numerics_digest.py:15](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:15) |

The inherited digest limits also remain: verifier arithmetic is excluded, the app closure follows functions rather than arbitrary module data, equivalence requires an explanation rather than automated proof, and history protection depends on `main` having a manifest. [test_numerics_version.py:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:69), [numerics_digest.py:109](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:109), [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

**2. Deployment and mixed-worker correctness**

- **MAJOR — automatic rechecking remains unbounded with concurrent checks.** With two installed seals, discovery of B launches two checks. A B response settles B; an A response from the other check then changes the epoch and launches two more checks. Repeat symmetrically. I reproduced **19 requests, nine epoch changes, two pending requests, and `_numericsSplit === false`**, stopping the probe deliberately. Every matching reply replenishes the opportunity for another automatic change. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102), [index.html:9118](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9118)

- **MAJOR — a split can still display CURRENT and accept a staged commit.** `_commitStaged` does not reject `_numericsSplit`, and `sealedState` reads the cache before checking split state. Reproducer: a staged B answer discovers B; a subsequent A reply causes a split; committing the previously answered B transaction returns `committed: true`, and its installed seal reads `current` while `_numericsSplit` remains true. This violates the explicit split behavior. [index.html:9209](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9209), [index.html:9284](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9284)

- **MAJOR — staged answers can be reused across epochs.** Answers retain an arrival-time `outdated` boolean, but no epoch. `_verdictEntry` assigns the epoch at aggregation. I reproduced: anchor answered under A in epoch 0; discover and settle B; discover and settle A in epoch 2; final answer under A; commit returns `consistent` without rechecking the anchor. The old answer has effectively been relabeled as belonging to epoch 2. Unreachable outcomes likewise lack epoch provenance. [index.html:9073](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9073), [index.html:9135](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9135), [index.html:9149](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9149)

Thus, the page can show confirmation without a fresh check of every constituent in the current epoch, and automatic rechecking can remain unbounded. I found **no irrecoverable seal once workers settle**: “check again” clears the split and supersedes the owner’s attempt. [index.html:9249](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9249)

**3. Server form completeness**

**MINOR — background-effect form remains incomplete.** `_BG_EFFECT_T` accepts arbitrary-length windows and anchor arrays, and makes method-specific fields optional. The producer emits two-element windows and two-element anchor coordinates. These shapes can be checked without recomputation. [fitting.py:3339](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3339), [fitting.py:2179](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:2179)

I reproduced `response_form_failure(...) == None` for a missing Shirley window, `window: [0]`, and malformed manual anchor coordinates. Paired with other numerics and an unreadable request, each returned `unconfirmed/numerics`, rather than `mismatch/schema`.

The reported round-3 field types and finiteness precedence are fixed. No honest-record rejection was found in the exercised cases.

**4. Test sensitivity and regressions**

The five new field tests **all failed with the round-3 form checker restored in memory**. The finiteness-order test failed with the round-3 route restored. The recording test rejected deliberately incorrect asteval and BLAS identities.

**MINOR — the epoch test does not detect removal of the epoch guard.** Its assertions observe the split and the completed retry, but miss the interval during retry. Removing `v.epoch === _numericsEpoch` preserves those observed end states; my probe showed an old confirmation appearing during that interval. The alternating-worker test exercises one seal, missing the concurrent settlement/redeployment cycle above. [test_browser_seal_step4.py:731](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:731), [test_browser_seal_step4.py:744](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:744)

Read-only validation: **100 JavaScript tests passed; 14 digest tests passed, one skipped; five recording cases passed; 90 verifier cases and 22 honest-record cases passed through the real endpoint using in-memory fits.** Page defects were reproduced with actual manager functions and controlled transport/ownership. Full Playwright integration and the historical 1b corpus were not run. Checkout unchanged.

VERDICT: NO-GO
